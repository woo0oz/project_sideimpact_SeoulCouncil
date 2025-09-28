"""
서울시 구의회 회의록 안건 추출 및 분석 시스템 (15,000자 제한 버전)

주요 특징:
1. Google Custom Search API 제거
2. agenda_full_text: 안건별 전체 내용 포함
3. agenda_url: comm_id 기반 회의록 URL 매핑
4. 토큰 제한: 회의록 내용을 15,000자로 제한하여 안정적 처리

사용 권장:
- 빠른 프로토타이핑
- API 비용 절약
- 안정적인 처리가 우선인 경우

입력: raw_content 폴더의 JSON 파일들 + tb_meta_info.json
출력: output_content 폴더의 처리된 JSON 파일들

환경변수 설정:
- OPENAI_API_KEY: OpenAI API 키
"""

import pandas as pd
import json
import re
import os
import time
import glob
from openai import OpenAI

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = "gpt-4o-mini"

def get_district_name_from_comm_id(comm_id):
    """회의록 ID에서 구 이름을 추출합니다."""
    district_mapping = {
        'gj': '광진구',
        'gn': '강남구', 
        'gr': '구로구',
        'gs': '강서구',
        'db': '도봉구',
        'dm': '동대문구',
        'gb': '강북구',
        'gc': '금천구',
        'gd': '강동구'
    }
    
    # comm_id에서 맨 앞 2글자 추출
    if len(comm_id) >= 2:
        district_code = comm_id[:2].lower()
        return district_mapping.get(district_code, '알 수 없는 구')
    
    return '알 수 없는 구'

def load_meta_info(meta_file_path):
    """tb_meta_info.json에서 comm_id와 URL 매핑을 로드합니다."""
    print(f"📂 메타 정보 로드 중: {meta_file_path}")
    
    with open(meta_file_path, 'r', encoding='utf-8') as file:
        meta_data = json.load(file)
    
    # comm_id를 키로 하는 딕셔너리 생성
    comm_id_to_url = {}
    for item in meta_data:
        comm_id = item.get('comm_id', '').strip()
        url = item.get('url', '').strip()
        # comm_id와 url이 모두 유효하고, 헤더 행이 아닌 경우만 추가
        if comm_id and url and comm_id != 'comm_id' and url != 'url':
            comm_id_to_url[comm_id] = url
    
    print(f"✅ 메타 정보 로드 완료: {len(comm_id_to_url)}개 comm_id")
    return comm_id_to_url

def load_data_from_json(json_file_path):
    """JSON 파일에서 데이터를 로드합니다."""
    print(f"📂 {json_file_path} 파일을 로드 중...")
    
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    processed_data = []
    for item in data:
        try:
            # raw_content가 문자열로 되어있는 경우 JSON 파싱
            if isinstance(item.get('raw_content'), str):
                raw_content = json.loads(item['raw_content'])
            else:
                raw_content = item.get('raw_content', {})
            
            processed_item = {
                'comm_id': raw_content.get('comm_id', ''),
                'content': raw_content.get('content', '')
            }
            processed_data.append(processed_item)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 에러: {e}")
            continue
    
    print(f"✅ 총 {len(processed_data)}개의 회의록 데이터 로드 완료")
    return processed_data

def extract_all_agendas_with_gpt(content, comm_id):
    """GPT를 사용하여 회의록 전체에서 모든 안건을 한 번에 추출합니다."""
    
    print(f"📄 전체 회의록 내용을 한 번에 처리합니다: {len(content):,}자")
    
    # 토큰 제한 무시하고 전체 내용 처리
    return extract_agendas_from_chunk(content, comm_id, 1)

def extract_agendas_from_chunk(content, comm_id, chunk_idx):
    """단일 청크에서 안건을 추출합니다."""
    
    prompt = f"""
다음은 서울시 구의회 회의록 내용입니다. 이 회의록에서 모든 안건을 찾아서 각각의 정보를 추출해주세요.

회의록 내용:
{content}

다음 형식으로만 응답해주세요 (JSON 배열 형태):
[
  {{
    "agenda_title": "안건의 정확한 제목",
    "agenda_summary": "안건의 상세한 배경과 목적을 포함한 요약",
    "agenda_impact": "이 안건이 시민들에게 미치는 영향을 요 체로 쉽게 설명",
    "agenda_interests": ["관련 분야 (교육, 문화, 복지, 환경, 교통, 안전, 경제, 보건 중 1-2개)"],
    "agenda_full_text": "해당 안건과 관련된 회의록의 모든 내용을 상세히 포함. 안건 제안자, 안건의 배경과 목적, 주요 내용, 질의응답, 토론 과정, 심사 결과, 가결/부결 여부 등 모든 세부사항을 포함해주세요."
  }}
]

안건 추출 기준:
1. 조례안, 예산안, 동의안, 승인안, 결의안 등 정식 의안
2. 구정질문, 긴급현안질문 등 정책 관련 질의
3. 5분 자유발언 중 정책 제안이나 현안 이슈
4. 제외할 것: 회기결정, 서명의원 선출, 위원 선임 등 절차적 안건

특히 agenda_full_text에는:
- 안건 제안자 및 발의자 정보
- 안건의 상세한 배경 설명
- 안건의 주요 내용과 목적
- 위원회에서의 질의응답 내용
- 찬반 토론 과정
- 심사 결과 (재석위원 수, 찬성/반대 수)
- 가결/부결 여부
등 해당 안건과 관련된 모든 회의록 내용을 빠짐없이 포함해주세요.
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )
        
        response_text = response.choices[0].message.content
        print(f"🔍 GPT 응답 길이: {len(response_text)}자")
        print(f"🔍 GPT 응답 앞부분: {response_text[:300]}...")
        
        # JSON 형태로 파싱 시도
        try:
            # JSON 블록 추출 (```json 또는 ``` 코드 블록 처리)
            if '```json' in response_text:
                print("🔍 ```json 블록 찾음")
                # ```json 이후부터 ``` 이전까지 추출
                start_idx = response_text.find('```json') + 7
                end_idx = response_text.find('```', start_idx)
                if end_idx != -1:
                    json_text = response_text[start_idx:end_idx].strip()
                    print(f"🔍 JSON 텍스트 추출 성공: {len(json_text)}자")
                else:
                    print("❌ ```json 블록의 끝을 찾을 수 없습니다!")
                    return []
            elif '```' in response_text:
                print("🔍 ``` 블록 찾음")
                start_idx = response_text.find('```') + 3
                end_idx = response_text.find('```', start_idx)
                if end_idx != -1:
                    json_text = response_text[start_idx:end_idx].strip()
                    print(f"🔍 JSON 텍스트 추출 성공: {len(json_text)}자")
                else:
                    print("❌ ``` 블록의 끝을 찾을 수 없습니다!")
                    return []
            else:
                print("🔍 일반 JSON 배열 찾기 시도")
                # [ 로 시작해서 ] 로 끝나는 부분 찾기
                start_idx = response_text.find('[')
                if start_idx != -1:
                    # 간단하게 전체 텍스트에서 JSON 부분만 추출
                    json_text = response_text[start_idx:].strip()
                    print(f"🔍 JSON 텍스트 추출 성공: {len(json_text)}자")
                else:
                    print("❌ JSON 배열을 찾을 수 없습니다!")
                    return []
            
            print(f"🔍 JSON 텍스트 앞부분: {json_text[:200]}...")
            print(f"🔍 JSON 텍스트 뒷부분: ...{json_text[-200:]}")
                parsing_attempts = [
                    # 1. 원본 그대로
                    lambda x: json.loads(x),
                    # 2. 기본적인 공백 정리
                    lambda x: json.loads(re.sub(r'\s+', ' ', x.strip())),
                    # 3. trailing comma 제거 + 줄바꿈 정리
                    lambda x: json.loads(re.sub(r',\s*}', '}', re.sub(r',\s*\]', ']', re.sub(r'(?<!")(\n\s*)(?!")', ' ', x.strip())))),
                    # 4. 더 적극적인 정리
                    lambda x: json.loads(re.sub(r',(\s*[}\]])', r'\1', re.sub(r'\s+', ' ', x.strip())))
                ]
                
                agendas = None
                for i, attempt in enumerate(parsing_attempts, 1):
                    try:
                        agendas = attempt(json_text)
                        if i > 1:
                            print(f"🔧 JSON 파싱 성공 (시도 {i}번째)")
                        break
                    except json.JSONDecodeError as e:
                        if i < len(parsing_attempts):
                            continue
                        else:
                            print(f"⚠️ 모든 JSON 파싱 시도 실패. 마지막 에러: {e}")
                            print(f"🔍 JSON 텍스트 일부: {json_text[:500]}...")
                            return []
                
                # agendas가 파싱되었는지 확인하고 디버그 정보 출력
                if agendas:
                    print(f"📋 파싱된 안건 수: {len(agendas)}")
                    for i, agenda in enumerate(agendas, 1):
                        full_text = agenda.get('agenda_full_text', '')
                        print(f"   안건 {i} agenda_full_text 길이: {len(full_text)}자")
                        if len(full_text) > 0:
                            print(f"   샘플: {full_text[:50]}...")
                else:
                    print("❌ agendas 파싱 결과가 None입니다!")
                    return []
                
                # 절차적 안건 필터링
                filtered_agendas = []
                for agenda in agendas:
                    if not is_procedural_agenda(agenda['agenda_title']):
                        filtered_agendas.append(agenda)
                    else:
                        print(f"🔄 절차적 안건 제외: {agenda['agenda_title']}")
                
                return filtered_agendas
            else:
                print("❌ JSON 블록을 찾을 수 없습니다!")
                print(f"🔍 응답 텍스트에 ```json 포함: {'```json' in response_text}")
                print(f"🔍 응답 텍스트에 ``` 포함: {'```' in response_text}")
                print(f"🔍 응답 텍스트에 [ 포함: {'[' in response_text}")
                return []
        except json.JSONDecodeError as e:
            print(f"⚠️ GPT 응답 JSON 파싱 실패: {e}")
            print(f"🔍 응답 텍스트 일부: {response_text[:500]}")
            return []
            
    except Exception as e:
        print(f"❌ GPT 안건 추출 실패: {e}")
        return []
    
    return []

def is_procedural_agenda(title):
    """절차적 안건인지 판단합니다."""
    procedural_keywords = [
        '회기', '의사일정', '서명의원', '위원장 선출', '부위원장 선출', 
        '위원 선임', '위원장 선거', '부의장 선거', '의장 선거',
        '서명의원 선출', '회의록 서명', '간사 선임',
        '서명의원 선임', '의사일정', '회의 중단', '회의 재개',
        '위원장 선출', '부위원장 선출', '간사 선임'
    ]
    
    return any(keyword in title for keyword in procedural_keywords)

def save_results_to_json(results, output_file_path):
    """결과를 JSON 파일로 저장합니다."""
    print(f"💾 결과를 {output_file_path}에 저장 중...")
    
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장 완료: {len(results)}개 안건")

def generate_agenda_id(comm_id, index):
    """comm_id 기반으로 고유한 agenda_id를 생성합니다."""
    return f"{comm_id}_{index:03d}"

def main_pipeline(json_file_path, output_path, comm_id_to_url):
    """전체 파이프라인을 실행합니다."""
    file_start_time = time.time()
    filename = os.path.basename(json_file_path).replace('.json', '')
    print(f"\n🚀 파일 처리 시작: {filename}")
    
    # 1. 데이터 로드
    data = load_data_from_json(json_file_path)
    
    all_results = []
    total_meetings = len(data)
    total_agendas_found = 0
    total_agendas_processed = 0
    
    # 전체 회의록 처리
    print(f"📊 총 {total_meetings}개의 회의록 처리를 시작합니다.")
    
    for meeting_idx, meeting in enumerate(data, 1):
        meeting_start_time = time.time()
        comm_id = meeting['comm_id']
        content = meeting['content']
        
        # 구 이름 추출
        district_name = get_district_name_from_comm_id(comm_id)
        
        print(f"\n--- {meeting_idx}/{total_meetings} 회의록 처리 시작 (회의록ID: {comm_id}, 구의회: {district_name}) ---")
        
        # 2. GPT를 사용하여 회의록 전체에서 모든 안건 추출
        extracted_agendas = extract_all_agendas_with_gpt(content, comm_id)
        
        if not extracted_agendas:
            print("⚠️ 추출된 안건이 없습니다.")
            meeting_elapsed = time.time() - meeting_start_time
            print(f"✅ {comm_id} 처리 완료 | 추출된 안건: 0개 | 소요시간: {meeting_elapsed:.2f}초")
            continue
        
        total_agendas_found += len(extracted_agendas)
        print(f"📑 회의록 {comm_id}에서 {len(extracted_agendas)}개의 안건을 추출했습니다.")
        
        # 3. 각 안건에 대해 결과 구성
        for agenda_idx, agenda_info in enumerate(extracted_agendas, 1):
            agenda_title = agenda_info['agenda_title']
            
            print(f"📄 안건 {agenda_idx}: '{agenda_title}' 처리 중...")
            
            # comm_id로 회의록 URL 찾기
            agenda_url = comm_id_to_url.get(comm_id, "")
            if agenda_url:
                print(f"🔗 회의록 URL: {agenda_url}")
            else:
                print(f"⚠️ comm_id {comm_id}에 해당하는 URL을 찾을 수 없습니다.")
                agenda_url = ""  # 명시적으로 빈 문자열 설정
            
            # agenda_full_text는 agenda_full_text 사용
            agenda_full_text = agenda_info.get('agenda_full_text', '')
            
            # 결과 구성
            result_item = {
                "comm_id": comm_id,
                "value": {
                    "agenda_id": generate_agenda_id(comm_id, agenda_idx),
                    "agenda_title": agenda_title,
                    "agenda_summary": agenda_info.get('agenda_summary', ''),
                    "agenda_impact": agenda_info.get('agenda_impact', ''),
                    "agenda_interests": agenda_info.get('agenda_interests', []),
                    "agenda_full_text": agenda_full_text,
                    "agenda_url": agenda_url
                }
            }
            
            all_results.append(result_item)
            total_agendas_processed += 1
            
            print(f"✅ 안건 처리 완료: {agenda_title[:50]}...")
            print(f"📄 안건 내용 길이: {len(agenda_full_text):,}자")
        
        meeting_elapsed = time.time() - meeting_start_time
        print(f"✅ {comm_id} 처리 완료 | 추출된 안건: {len(extracted_agendas)}개 | 소요시간: {meeting_elapsed:.2f}초")
    
    # 4. 결과 저장
    output_file_path = os.path.join(output_path, f"{filename}_prep.json")
    save_results_to_json(all_results, output_file_path)
    
    # 통계 출력
    file_elapsed = time.time() - file_start_time
    print(f"\n📊 파일 처리 완료 통계:")
    print(f"   • 파일명: {filename}")
    print(f"   • 처리된 회의록: {total_meetings}개")
    print(f"   • 발견된 총 안건: {total_agendas_found}개")
    print(f"   • 처리된 총 안건: {total_agendas_processed}개")
    print(f"   • 총 소요시간: {file_elapsed:.2f}초")
    print(f"   • 회의록당 평균 시간: {file_elapsed/total_meetings:.2f}초")
    print(f"   • 출력 파일: {output_file_path}")

def main():
    """메인 실행 함수"""
    # 폴더 경로 설정
    input_folder = "raw_content"
    output_folder = "output_content"
    meta_file_path = os.path.join(input_folder, "tb_meta_info.json")
    
    print("🔍 서울시 구의회 회의록 처리 시스템 (간소화 버전)")
    print("="*60)
    
    # 메타 정보 로드
    if not os.path.exists(meta_file_path):
        print(f"❌ 메타 정보 파일을 찾을 수 없습니다: {meta_file_path}")
        exit(1)
    
    comm_id_to_url = load_meta_info(meta_file_path)
    
    # 출력 폴더 생성
    os.makedirs(output_folder, exist_ok=True)
    
    # JSON 파일 찾기 (메타 파일 제외)
    json_files = [f for f in glob.glob(os.path.join(input_folder, "*.json")) 
                  if not f.endswith("tb_meta_info.json")]
    
    if not json_files:
        print(f"❌ {input_folder} 폴더에 처리할 JSON 파일이 없습니다.")
        exit(1)
    
    total_start_time = time.time()
    print(f"🎯 전체 처리 시작: {len(json_files)}개 파일")
    
    # 각 JSON 파일 처리
    for file_idx, json_file_path in enumerate(json_files, 1):
        print(f"\n{'='*60}")
        
        # 파일명에서 구 코드 추출
        filename = os.path.basename(json_file_path).replace('.json', '')
        district_code = filename.split('_')[-1] if '_' in filename else filename[:2]
        district_name = get_district_name_from_comm_id(district_code)
        
        print(f"📁 {file_idx}/{len(json_files)} 파일 처리 중... ({district_name})")
        main_pipeline(json_file_path, output_folder, comm_id_to_url)
    
    # 전체 완료 통계
    total_elapsed = time.time() - total_start_time
    print(f"\n{'='*60}")
    print(f"🎉 전체 처리 완료!")
    print(f"   • 총 파일 수: {len(json_files)}개")
    print(f"   • 총 소요시간: {total_elapsed:.2f}초")
    print(f"   • 평균 파일당 시간: {total_elapsed/len(json_files):.2f}초")
    print(f"   • 결과 저장 폴더: {output_folder}")

if __name__ == "__main__":
    """
    실행 방법:
    1. 필수 환경변수 설정:
       - OPENAI_API_KEY: OpenAI API 키
    
    2. 필수 파일 확인:
       - raw_content/ 폴더에 JSON 파일들
       - raw_content/tb_meta_info.json (comm_id와 URL 매핑)
    
    3. 실행:
       python meeting_minutes_processor_simple.py
    """
    
    # 환경변수 확인
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   Windows: set OPENAI_API_KEY=your-api-key")
        print("   Linux/Mac: export OPENAI_API_KEY=your-api-key")
        exit(1)
    
    main()