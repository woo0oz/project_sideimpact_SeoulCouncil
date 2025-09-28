import pandas as pd
import os
import re
import json
import time
from openai import OpenAI
from typing import List, Dict, Any

# --- 1. 설정 (Configuration) ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL_NAME = "gpt-5-mini"
# MODEL_NAME = "gpt-3.5-turbo"
# MODEL_NAME = "gpt-4o"

def load_data_from_json(filepath: str) -> List[Dict[str, Any]]:
    """JSON 파일로부터 데이터를 로드합니다."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # JSON 데이터가 리스트인지 확인
        if isinstance(data, list):
            print(f"✅ '{filepath}'에서 {len(data)}개의 회의록을 성공적으로 로드했습니다.")
            return data
        elif isinstance(data, dict):
            # 단일 객체인 경우 리스트로 감싸기
            print(f"✅ '{filepath}'에서 1개의 회의록을 성공적으로 로드했습니다.")
            return [data]
        else:
            print(f"❌ 에러: JSON 파일 형식이 올바르지 않습니다 - {filepath}")
            return []
    except FileNotFoundError:
        print(f"❌ 에러: 파일을 찾을 수 없습니다 - {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ 에러: JSON 파싱 실패 - {e}")
        return []

# --- 회의 전체 단위 안건 추출 ---
def extract_agendas_from_meeting(content: str, comm_id: str = "unknown") -> List[str]:
    """
    회의 전체 텍스트에서 '의사일정 제x항 ...' 패턴을 찾아
    안건별 구간을 리스트로 반환
    """
    # 더 포괄적인 안건 패턴들을 시도
    patterns = [
        # 기본 패턴: 의사일정 제x항 ... 의 건/안
        r"(의사일정\s*제?\d+항\s*.+?(?:의 건|조례안|동의안|수정안|의안))",
        # 대안 패턴: 제x호 의안, 제x항 등
        r"(제\d+호\s*의안\s*.+?(?:의 건|조례안|동의안|수정안|의안))",
        # 더 넓은 패턴: ...의 건, ...안으로 끝나는 제목들
        r"([가-힣\s\d]+(?:의 건|조례안|동의안|수정안|의안))"
    ]
    
    all_matches = []
    for pattern in patterns:
        compiled_pattern = re.compile(pattern)
        matches = list(compiled_pattern.finditer(content))
        all_matches.extend(matches)
    
    # 중복 제거 및 정렬
    unique_matches = []
    seen_positions = set()
    for match in sorted(all_matches, key=lambda x: x.start()):
        if match.start() not in seen_positions:
            unique_matches.append(match)
            seen_positions.add(match.start())
    
    if not unique_matches:
        print(f"⚠️ 회의록 {comm_id}에서 안건 후보를 찾지 못했습니다.")
        # 패턴이 없을 때 대안: 전체 텍스트를 하나의 안건으로 처리
        if content.strip():
            print("  📝 전체 내용을 단일 안건으로 처리합니다.")
            return [content.strip()]
        return []

    agendas_with_context = []
    for i, match in enumerate(unique_matches):
        start = match.start()
        # 다음 안건까지 또는 텍스트 끝까지
        end = unique_matches[i + 1].start() if i + 1 < len(unique_matches) else len(content)
        agenda_text = content[start:end].strip()
        
        # 너무 짧은 안건은 제외 (50자 미만)
        if len(agenda_text) >= 50:
            agendas_with_context.append(agenda_text)

    print(f"📑 회의록 {comm_id}에서 {len(agendas_with_context)}개의 안건 구간을 탐지했습니다.")
    return agendas_with_context


def extract_info_with_gpt(agenda_text: str, comm_id: str = "unknown") -> List[Dict[str, Any]]:
    """
    GPT API에 안건 텍스트를 넣고,
    안건명/요약/관심사를 JSON 형식으로 추출
    """
    system_prompt = f"""
    당신은 대한민국 서울시 구의회 회의록을 분석하는 전문가입니다. 
당신의 임무는 주어진 회의록 구간에서 반드시 '안건' 정보를 식별하고, 이를 JSON 배열로 구조화하는 것입니다.

# 역할
- 회의록 전문을 읽고 '의사일정 제x항 ...의 건/안'과 같은 표현을 기반으로 안건을 식별합니다.
- 안건은 반드시 하나 이상 존재한다고 가정하세요. 따라서 절대로 빈 리스트 [] 를 출력하지 마세요.

# 안건 정의
- '...의 건', '...안', '...조례안', '...동의안', '...수정안', '...의안' 등으로 끝나는 구문은 모두 안건입니다.
- '의사일정 제x항 ...의 건' 같은 표현도 반드시 안건입니다.
- 한 구간에 여러 개 안건이 있을 수 있으며, 나열된 모든 안건을 각각 별도의 JSON 객체로 추출해야 합니다.

# 출력 형식
- 반드시 JSON 배열만 출력하세요. 설명, 문장, 주석은 절대 포함하지 마세요.
- JSON 배열 안에는 하나 이상의 안건 객체가 들어가야 합니다.
- 각 안건 객체는 다음 필드를 반드시 포함합니다:
  - "안건명": 안건의 제목 (원문 그대로 또는 필요한 최소 수정만)
  - "안건 내용 요약": 안건의 핵심을 3줄 이내로 요약. 처리 결과(가결/부결/채택/보류 등)가 있다면 반드시 포함.
  - "관심사": 아래 카테고리 중에서 선택 (최소 1개, 최대 3개):
    ["교통","환경","복지","경제","교육","안전","문화","보건"]
    * 원칙: 가능한 한 1개로 분류
    * 예외: 안건이 명확히 여러 분야에 걸친 경우에만 2~3개 허용
    * 형식: 단일 분야면 ["환경"] 배열, 복수 분야면 ["환경","경제"] 배열로 출력

# 출력 예시
[
  {{
    "안건명": "한국성서대학교 도시관리계획(용도지역) 변경을 위한 구의회 의견제시의 건",
    "안건 내용 요약": "한국성서대학교 부지 내 용도지역 경계를 정형화하여 효율적 관리. 찬성의견 채택.",
    "관심사": ["환경"]
  }},
  {{
    "안건명": "서울특별시 노원구 노점상 자립지원을 위한 기금 설치 및 운용 조례 일부개정조례안",
    "안건 내용 요약": "노점상 자립 지원을 위한 기금 설치·운용 조례 개정안. 위원회 심사 완료.",
    "관심사": ["경제"]
  }},
  {{
    "안건명": "청소년 교통안전 교육 및 환경보호 프로그램 운영 조례안",
    "안건 내용 요약": "청소년 대상 교통안전 교육과 환경보호 활동을 통합 운영하는 조례안. 교육청과 환경부서 협력 추진.",
    "관심사": ["교육","교통","환경"]
  }}
]
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": agenda_text}
            ]
        )

        content = response.choices[0].message.content.strip()
        print("🔎 GPT 원본 응답:", content[:200], "...")  # <- 디버깅용 (앞부분만 출력)

        parsed_json = json.loads(content)
        if isinstance(parsed_json, dict):
            for key, value in parsed_json.items():
                if isinstance(value, list):
                    return value
            return []
        return parsed_json

    except Exception as e:
        print(f"❌ GPT API 호출 또는 JSON 파싱 중 에러 발생: {e}")
        return []


# --- 회의 진행 관련 안건 필터링 함수 ---
def is_procedural_agenda(agenda_title: str) -> bool:
    """회의 진행과 관련된 안건인지 판단하는 함수"""
    if not agenda_title:
        return False
    
    # 제외할 키워드들
    procedural_keywords = [
        "회의 휴회의 건", "본회의 휴회의 건", "휴회의 건",
        "회의록 서명의원 선임의 건", "서명의원 선임의 건",
        "임시회 회기 결정의 건", "회기 결정의 건",
        "정례회 회기 결정의 건", "본회의 회기 결정의 건",
        "의사일정", "성원확인", "개의선포",
        "산회", "폐회", "개회"
    ]
    
    for keyword in procedural_keywords:
        if keyword in agenda_title:
            return True
    
    return False


# --- 저장 함수 (JSON 버전) ---
def save_results_to_json(results: List[Dict[str, Any]], output_filename: str):
    """처리된 최종 결과를 JSON 파일로 저장"""
    if not results:
        print("⚠️ 저장할 데이터가 없습니다.")
        return
    try:
        with open(output_filename, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=2)
        print(f"\n💾 최종 결과를 '{output_filename}' 파일로 성공적으로 저장했습니다.")
    except Exception as e:
        print(f"❌ JSON 파일 저장 중 에러 발생: {e}")

# --- 메인 파이프라인 (JSON 버전) ---
def main_pipeline(filepath: str, output_filepath: str):
    data = load_data_from_json(filepath)
    if not data:
        return

    final_results = []
    total_start_time = time.time()

    print(f"� 전체 데이터 처리 시작: {len(data)}개 회의록을 처리합니다.")

    for index, row in enumerate(data):
        # raw_content가 있는 경우 JSON 파싱 처리
        if 'raw_content' in row:
            try:
                raw_data = json.loads(row['raw_content'])
                comm_id = raw_data.get('comm_id', f'unknown_{index+1}')
                content = raw_data.get('content', '')
            except json.JSONDecodeError:
                print(f"❌ {index+1}번째 데이터 JSON 파싱 실패")
                continue
        else:
            # 기존 형식 지원
            comm_id = row.get('comm_id', f'unknown_{index+1}')  
            content = row.get('content', '')
        
        meeting_start_time = time.time()
        print(f"\n--- {index + 1}/{len(data)} 회의록 처리 시작 (회의록ID: {comm_id}) ---")

        # content 길이 체크
        if not content or len(content.strip()) < 100:
            meeting_elapsed = time.time() - meeting_start_time
            print(f"  ⚠️ 내용이 너무 짧습니다 (길이: {len(content)}) | 소요시간: {meeting_elapsed:.2f}초")
            continue

        # 지역구 추출 - content에서 직접 추출
        district_match = re.search(r'(\w+)구의회', content)
        district = district_match.group(1) if district_match else "알수없음"

        # 회의 전체에서 안건별 구간 추출
        agenda_contexts = extract_agendas_from_meeting(content, comm_id)

        # 안건별 GPT 분석
        agenda_counter = 1  # 각 회의록별로 안건 번호 초기화
        for agenda_text in agenda_contexts:
            extracted_agendas = extract_info_with_gpt(agenda_text, comm_id)
            if not extracted_agendas:
                print("  ⚠️ 해당 구간에서 안건을 찾지 못했습니다.")
                continue

            for agenda in extracted_agendas:
                # 회의 진행 관련 안건 필터링
                agenda_title = agenda.get("안건명", "")
                if is_procedural_agenda(agenda_title):
                    print(f"  🚫 회의 진행 관련 안건 제외: {agenda_title}")
                    continue
                
                processed_agenda = {
                    "comm_id": comm_id,
                    "value": {
                        "agenda_id": f"{comm_id}_{agenda_counter:03d}",
                        "agenda_title": agenda_title,
                        "agenda_summary": agenda.get("안건 내용 요약"),
                        "agenda_interests": agenda.get("관심사", [])
                    }
                }
                final_results.append(processed_agenda)
                agenda_counter += 1

        # 회의록별 처리 완료 로그
        meeting_elapsed = time.time() - meeting_start_time
        extracted_count = agenda_counter - 1  # 현재 회의록에서 추출된 안건 수
        print(f"✅ {comm_id} 처리 완료 | 추출된 안건: {extracted_count}개 | 소요시간: {meeting_elapsed:.2f}초")

    # 전체 처리 완료 로그
    total_elapsed = time.time() - total_start_time
    print(f"\n{'='*60}")
    print(f"✅ 모든 전처리 파이프라인이 완료되었습니다!")
    print(f"📊 처리 결과:")
    print(f"   - 총 회의록 수: {len(data)}개")
    print(f"   - 총 추출된 안건 수: {len(final_results)}개")
    print(f"   - 전체 소요시간: {total_elapsed:.2f}초 ({total_elapsed/60:.1f}분)")
    print(f"   - 회의록당 평균 처리시간: {total_elapsed/len(data):.2f}초")
    print(f"{'='*60}")

    # 예시 출력
    for result in final_results[:3]:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("-" * 20)

    save_results_to_json(final_results, output_filepath)

# --- 스크립트 실행 ---
if __name__ == "__main__":
    import os
    import glob
    
    # 폴더 경로 설정
    raw_content_folder = "raw_content"
    output_folder = "output_content"
    
    # output 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 {output_folder} 폴더를 생성했습니다.")
    
    # raw_content 폴더에서 JSON 파일들 찾기
    json_files = glob.glob(os.path.join(raw_content_folder, "*.json"))
    
    if not json_files:
        print(f"❌ {raw_content_folder} 폴더에서 JSON 파일을 찾을 수 없습니다.")
        exit(1)
    
    print(f"📂 {len(json_files)}개의 JSON 파일을 발견했습니다:")
    for file in json_files:
        print(f"  - {os.path.basename(file)}")
    
    # 각 파일을 순차적으로 처리
    total_files = len(json_files)
    overall_start_time = time.time()
    
    for file_index, json_file_path in enumerate(json_files, 1):
        input_filename = os.path.basename(json_file_path)
        filename_without_ext = os.path.splitext(input_filename)[0]
        output_filename = f"{filename_without_ext}_prep.json"
        output_path = os.path.join(output_folder, output_filename)
        
        file_start_time = time.time()
        print(f"\n{'='*60}")
        print(f"� 파일 {file_index}/{total_files} 처리 시작: {input_filename}")
        print(f"📤 출력 파일: {output_filename}")
        print(f"{'='*60}")
        
        main_pipeline(json_file_path, output_path)
        
        file_elapsed = time.time() - file_start_time
        print(f"\n📁 파일 {input_filename} 처리 완료 | 소요시간: {file_elapsed:.2f}초 ({file_elapsed/60:.1f}분)")
    
    # 전체 처리 완료 요약
    overall_elapsed = time.time() - overall_start_time
    print(f"\n{'🎉'*20}")
    print(f"🎉 전체 파일 처리 완료!")
    print(f"📊 최종 요약:")
    print(f"   - 처리된 파일 수: {total_files}개")
    print(f"   - 전체 소요시간: {overall_elapsed:.2f}초 ({overall_elapsed/60:.1f}분)")
    print(f"   - 파일당 평균 처리시간: {overall_elapsed/total_files:.2f}초")
    print(f"{'🎉'*20}")