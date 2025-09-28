"""
서울시 구의회 회의록 안건 추출 및 분석 시스템 (최종 버전)

주요 기능:
1. JSON 형태의 회의록 데이터 처리
2. GPT-4o-mini를 활용한 전체 문서 안건 추출
3. 8개 분야 자동 분류 (교육, 문화, 복지, 환경, 교통, 안전, 경제, 보건)
4. clik.nanet.go.kr에서 의안 공식 문서 매칭 및 URL 추출
5. 시민 친화적인 ~요 체 말투로 영향도 설명
6. 정제된 검색 결과 텍스트 제공

입력: raw_content 폴더의 JSON 파일들
출력: output_content 폴더의 처리된 JSON 파일들

환경변수 설정:
- OPENAI_API_KEY: OpenAI API 키
- GOOGLE_API_KEY: Google Custom Search API 키 (선택사항)
- SEARCH_ENGINE_ID: Google Custom Search Engine ID (선택사항)
"""

import pandas as pd
import json
import re
import os
import time
import glob
from openai import OpenAI
import requests
from urllib.parse import quote

# clik.nanet.go.kr 검색 헬퍼 import
from clik_search_helper import search_clik_with_filters, extract_district_from_title, get_bill_content

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = "gpt-4o-mini"

# Google Custom Search API 설정 (폴백용)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

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
    prompt = f"""
다음은 서울시 구의회 회의록 전체 내용입니다. 이 회의록에서 모든 안건을 찾아서 각각의 정보를 추출해주세요.

회의록 내용:
{content}

다음 형식으로만 응답해주세요 (JSON 배열 형태):
[
  {{
    "agenda_title": "안건 제목 (구체적이고 정확한 제목)",
    "agenda_summary": "안건의 상세 배경과 주요 내용을 포함한 요약 (3-4문장으로 구체적 사업내용, 예산, 일정, 대상지역 등 포함)",
    "agenda_impact": "해당 구 시민들에게 실제로 미치는 영향을 친근한 ~요 체로 설명 (예: '~할 수 있게 되어요', '~하게 됐어요', '~할 예정이에요' 등의 말투로 구체적 혜택과 변화사항 설명)",
    "agenda_interests": ["분야1", "분야2", "분야3"]
  }}
]

안건 분야는 다음 중에서 선택해주세요 (최소 1개, 최대 3개):
- 교육: 교육정책, 학교, 교육시설 관련
- 문화: 문화시설, 문화행사, 예술, 체육 관련  
- 복지: 사회복지, 노인복지, 장애인복지 관련
- 환경: 환경보호, 청소, 공원, 녹지 관련
- 교통: 교통정책, 도로, 주차, 대중교통 관련
- 안전: 치안, 방범, 안전시설, 재난대응 관련
- 경제: 경제정책, 지역경제, 상공업 지원 관련
- 보건: 보건의료, 의료시설, 건강증진 관련

분류 원칙:
* 가능한 한 1개 분야로 분류
* 안건이 명확히 여러 분야에 걸친 경우에만 2~3개 허용
* 형식: 단일 분야면 ["환경"] 배열, 복수 분야면 ["환경","경제"] 배열로 출력

주의사항:
1. 실제 안건만 추출하고, 절차적인 내용(회의 개회, 폐회, 서명의원 선임 등)은 제외
2. 같은 안건이 중복되지 않도록 주의
3. 안건이 없거나 추출할 수 없으면 빈 배열 []을 반환
4. 각 안건의 제목은 최대한 구체적이고 정확하게 작성
"""

    try:
        print(f"🤖 GPT를 사용하여 회의록 {comm_id} 전체 분석 중...")
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON 파싱 시도
        try:
            if result_text.lower() == '[]' or not result_text.strip():
                return []
            
            # 코드 블록 형태의 응답 처리
            if result_text.startswith('```json'):
                # ```json ... ``` 형태에서 JSON 부분 추출
                json_start = result_text.find('[')
                json_end = result_text.rfind(']') + 1
                if json_start != -1 and json_end != 0:
                    result_text = result_text[json_start:json_end]
                else:
                    print(f"⚠️ JSON 코드 블록에서 배열을 찾을 수 없음: {result_text[:100]}...")
                    return []
            
            # JSON 형태가 아닌 경우 처리
            if not result_text.startswith('['):
                print(f"⚠️ 예상하지 못한 응답 형식: {result_text[:100]}...")
                return []
            
            agendas = json.loads(result_text)
            
            # 결과 검증 및 정제
            valid_agendas = []
            for agenda in agendas:
                if isinstance(agenda, dict) and agenda.get('agenda_title') and agenda.get('agenda_summary') and agenda.get('agenda_impact'):
                    # 절차적 안건 필터링
                    if not is_procedural_agenda(agenda['agenda_title']):
                        valid_agendas.append(agenda)
                    else:
                        print(f"🔄 절차적 안건 제외: {agenda['agenda_title']}")
            
            print(f"✅ 총 {len(valid_agendas)}개의 유효한 안건 추출 완료")
            return valid_agendas
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 실패: {e}")
            print(f"응답 내용: {result_text[:200]}...")
            return []
            
    except Exception as e:
        print(f"❌ GPT API 호출 중 에러 발생: {e}")
        return []

def clean_search_text(text):
    """검색 결과 텍스트에서 불필요한 내용을 제거합니다."""
    import re
    from urllib.parse import unquote
    
    # URL 디코딩
    try:
        text = unquote(text, encoding='utf-8')
    except:
        pass
    
    # 불필요한 패턴 제거
    patterns_to_remove = [
        r'https?://[^\s]+',  # URL 제거
        r'www\.[^\s]+',      # www로 시작하는 도메인 제거
        r'%[0-9A-Fa-f]{2}',  # URL 인코딩 잔여물 제거
        r'[가-힣]*게임[가-힣]*',  # 게임 관련 광고 제거
        r'카지노|바카라|텍사스|포커',  # 도박 관련 광고 제거
        r'쇼핑몰|배송|주문|아마존|11번가',  # 쇼핑 관련 광고 제거
        r'AD[가-힣]*|광고[가-힣]*',  # 광고 표시 제거
        r'\s+',  # 연속된 공백을 하나로
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, ' ', text)
    
    # 한글, 숫자, 기본 문장부호만 유지
    text = re.sub(r'[^가-힣0-9a-zA-Z\s.,!?()·\-]', ' ', text)
    
    # 연속된 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 너무 짧거나 의미없는 텍스트 필터링
    if len(text) < 10 or not re.search(r'[가-힣]', text):
        return ""
    
    return text

def google_search(query, num_results=3):
    """Google Custom Search API를 사용하여 검색 결과를 가져옵니다."""
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("⚠️ Google API 키 또는 Search Engine ID가 설정되지 않았습니다.")
        return []
    
    try:
        # 검색 쿼리 정제
        clean_query = query.replace('조례안', '').replace('의건', '').strip()
        encoded_query = quote(clean_query)
        
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': SEARCH_ENGINE_ID,
            'q': encoded_query,
            'num': num_results,
            'lr': 'lang_ko',  # 한국어 결과만
            'hl': 'ko'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        search_results = response.json()
        
        # 검색 결과 정리 - snippet만 문자열로 합치기
        snippets = []
        if 'items' in search_results:
            for item in search_results['items']:
                snippet = item.get('snippet', '').strip()
                if snippet:  # 빈 snippet은 제외
                    # 텍스트 정제
                    cleaned_snippet = clean_search_text(snippet)
                    if cleaned_snippet:  # 정제 후에도 내용이 있으면
                        snippets.append(cleaned_snippet)
        
        # snippet들을 하나의 문자열로 합치기
        return ' '.join(snippets) if snippets else ""
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Google 검색 API 호출 실패: {e}")
        return []
    except Exception as e:
        print(f"⚠️ 검색 중 에러 발생: {e}")
        return []



def is_procedural_agenda(title):
    """절차적 안건인지 확인합니다."""
    procedural_keywords = [
        '회의록 서명', '회의 휴회', '회의 개회', '회의 속개', '회의 폐회',
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

def main_pipeline(json_file_path, output_path):
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
        
        print(f"📑 회의록 {comm_id}에서 {len(extracted_agendas)}개의 안건을 추출했습니다.")
        
        meeting_agendas = 0
        
        # 3. 각 안건에 대해 clik.nanet.go.kr에서 의안 검색 및 결과 구성
        for agenda_idx, agenda_info in enumerate(extracted_agendas, 1):
            agenda_title = agenda_info['agenda_title']
            
            print(f"🔍 '{agenda_title}' clik.nanet.go.kr에서 의안 검색 중...")
            
            # 구 이름 추출 (comm_id와 title 모두에서)
            district_from_id = get_district_name_from_comm_id(comm_id)
            district_from_title = extract_district_from_title(agenda_title)
            
            # comm_id 기반 구 이름을 우선 사용, 없으면 제목에서 추출
            district = district_from_title if district_from_title != "알 수 없는 구" else district_from_id
            
            print(f"🏢 대상 구의회: {district}")
            
            # clik.nanet.go.kr에서 의안 검색
            clik_result = search_clik_with_filters(agenda_title, district)
            
            agenda_url = ""
            agenda_full_text = ""
            
            if clik_result:
                agenda_url = clik_result['url']
                print(f"✅ 의안 매칭 성공: {clik_result['title']}")
                print(f"🔗 URL: {agenda_url}")
                
                # 의안 전문 내용 가져오기
                agenda_full_text = get_bill_content(agenda_url)
                if agenda_full_text:
                    print(f"📄 의안 내용 추출: {len(agenda_full_text)}자")
                else:
                    print("⚠️ 의안 내용 추출 실패 - 요약 정보 사용")
                    agenda_full_text = clik_result.get('summary', '')
            else:
                print("❌ 매칭되는 의안 없음 - Google Search로 폴백")
                
                # 폴백: Google Custom Search 사용
                if GOOGLE_API_KEY and SEARCH_ENGINE_ID:
                    search_results = google_search(agenda_title)
                    agenda_full_text = search_results
                else:
                    agenda_full_text = ""
            
            # 안건 ID 생성
            agenda_id = generate_agenda_id(comm_id, agenda_idx)
            
            # 결과 구성 (새로운 형식 - agenda_url 추가)
            result = {
                "comm_id": comm_id,
                "value": {
                    "agenda_id": agenda_id,
                    "agenda_title": agenda_title,
                    "agenda_summary": agenda_info['agenda_summary'],
                    "agenda_impact": agenda_info.get('agenda_impact', '시민들에게 긍정적인 영향을 미칠 것으로 예상됩니다.'),
                    "agenda_interests": agenda_info.get('agenda_interests', []),
                    "agenda_full_text": agenda_full_text,
                    "agenda_url": agenda_url
                }
            }
            
            all_results.append(result)
            meeting_agendas += 1
            total_agendas_processed += 1
            
            print(f"✅ 안건 처리 완료: {agenda_title[:50]}...")
            print(f"🔍 검색 결과: {len(agenda_full_text)}자")
        
        total_agendas_found += len(extracted_agendas)
        meeting_elapsed = time.time() - meeting_start_time
        print(f"✅ {comm_id} 처리 완료 | 추출된 안건: {meeting_agendas}개 | 소요시간: {meeting_elapsed:.2f}초")
    
    # 4. 결과 저장
    output_file_path = os.path.join(output_path, f"{filename}_prep.json")
    save_results_to_json(all_results, output_file_path)
    
    # 5. 최종 통계
    file_elapsed = time.time() - file_start_time
    print(f"\n📊 파일 처리 완료 통계:")
    print(f"   • 파일명: {filename}")
    print(f"   • 처리된 회의록: {total_meetings}개")
    print(f"   • 탐지된 안건 구간: {total_agendas_found}개")
    print(f"   • 처리된 안건: {total_agendas_processed}개")
    print(f"   • 총 소요시간: {file_elapsed:.2f}초")
    print(f"   • 저장 위치: {output_file_path}")

def main():
    """메인 실행 함수"""
    # 환경 변수 확인
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        exit(1)
    
    if not GOOGLE_API_KEY:
        print("⚠️ GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다. (폴백 검색 기능 비활성화)")
        
    if not SEARCH_ENGINE_ID:
        print("⚠️ SEARCH_ENGINE_ID 환경 변수가 설정되지 않았습니다. (폴백 검색 기능 비활성화)")
    
    print("🔍 clik.nanet.go.kr 의안 검색 기능 활성화")
    if GOOGLE_API_KEY and SEARCH_ENGINE_ID:
        print("✅ Google 검색 폴백 기능 활성화")
    else:
        print("⚠️ Google 검색 폴백 기능 비활성화")
    
    # 입력 및 출력 경로 설정
    input_folder = "raw_content"
    output_folder = "output_content"
    
    # 폴더가 없으면 생성
    os.makedirs(output_folder, exist_ok=True)
    
    # JSON 파일 찾기
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    
    if not json_files:
        print(f"❌ {input_folder} 폴더에 JSON 파일이 없습니다.")
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
        main_pipeline(json_file_path, output_folder)
    
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
       - OPENAI_API_KEY
    
    2. 선택적 환경변수 설정 (Google 검색 기능):
       - GOOGLE_API_KEY
       - SEARCH_ENGINE_ID
    
    3. 실행:
       python meeting_minutes_processor_with_search.py
    
    4. 결과 확인:
       output_content 폴더에서 *_prep.json 파일들 확인
    """
    main()