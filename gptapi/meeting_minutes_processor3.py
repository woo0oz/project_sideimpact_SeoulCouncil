import pandas as pd
import os
import re
import json
from openai import OpenAI
from typing import List, Dict, Any

# --- 1. 설정 (Configuration) ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL_NAME = "gpt-5-mini"
# MODEL_NAME = "gpt-3.5-turbo"
# MODEL_NAME = "gpt-4o"

def load_data_from_csv(filepath: str) -> pd.DataFrame:
    """CSV 파일로부터 데이터를 로드합니다."""
    try:
        df = pd.read_csv(filepath)
        print(f"✅ '{filepath}'에서 {len(df)}개의 회의록을 성공적으로 로드했습니다.")
        return df
    except FileNotFoundError:
        print(f"❌ 에러: 파일을 찾을 수 없습니다 - {filepath}")
        return pd.DataFrame()

# --- 회의 전체 단위 안건 추출 ---
def extract_agendas_from_meeting(content: str, district: str) -> List[str]:
    """
    회의 전체 텍스트에서 '의사일정 제x항 ...' 패턴을 찾아
    안건별 구간을 리스트로 반환
    """
    agenda_pattern = re.compile(r"(의사일정\s*제?\d+항\s*.+?(?:의 건|조례안|동의안|수정안|의안))")
    matches = list(agenda_pattern.finditer(content))

    if not matches:
        print("⚠️ 안건 후보를 찾지 못했습니다.")
        return []

    agendas_with_context = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        agenda_text = content[start:end].strip()
        agendas_with_context.append(agenda_text)

    print(f"📑 회의록에서 {len(agendas_with_context)}개의 안건 구간을 탐지했습니다.")
    return agendas_with_context


def extract_info_with_gpt(agenda_text: str, district: str) -> List[Dict[str, Any]]:
    """
    GPT API에 안건 텍스트를 넣고,
    안건명/요약/관심사를 JSON 형식으로 추출
    """
    system_prompt = f"""
    당신은 대한민국 서울시 {district} 구의회 회의록을 분석하는 전문가입니다.
    주어진 텍스트에는 반드시 1개 이상의 '안건'이 포함되어 있습니다.

    # 안건 식별 규칙
    - 안건은 '...의 건', '...조례안', '...동의안', '...수정안', '...의안' 등의 형태로 나타납니다.
    - '의사일정 제x항 ...' 구문은 반드시 안건입니다.
    - 여러 안건이 있으면 모두 별도의 JSON 객체로 추출하세요.
    - 안건 처리 결과(가결, 부결, 채택 등)는 '안건 내용 요약'에 반드시 포함하세요.
    - '관심사'는 ["교통","환경","복지","경제","교육","안전","문화","보건"] 중 하나만 선택하세요.

    # 출력 규칙
    - 반드시 JSON 배열 형식만 출력하세요.
    - 예시:
    [
      {{
        "안건명": "구립하계지역아동센터 운영사무의 민간위탁 재위탁 동의안",
        "안건 내용 요약": "구립하계지역아동센터의 운영을 민간에 재위탁하는 안건. 원안 가결됨.",
        "관심사": "복지"
      }}
    ]
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": agenda_text}
            ],
            # temperature=0.2,
            # max_tokens=1500
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


# --- 저장 함수 ---
def save_results_to_csv(results: List[Dict[str, Any]], output_filename: str):
    """처리된 최종 결과를 CSV 파일로 저장"""
    if not results:
        print("⚠️ 저장할 데이터가 없습니다.")
        return
    try:
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_filename, index=False, encoding="utf-8-sig")
        print(f"\n💾 최종 결과를 '{output_filename}' 파일로 성공적으로 저장했습니다.")
    except Exception as e:
        print(f"❌ CSV 파일 저장 중 에러 발생: {e}")

# --- 메인 파이프라인 ---
def main_pipeline(filepath: str, output_filepath: str):
    df = load_data_from_csv(filepath)
    if df.empty:
        return

    final_results = []
    agenda_id_counter = 1

    for index, row in df.iterrows():
        print(f"\n--- {index + 1}번째 회의록 처리 시작 (회의: {row['session']}, 차수: {row['sitting']}) ---")

        # 지역구 추출
        district_match = re.search(r'(\w+)구의회', row['title'])
        district = district_match.group(1) if district_match else "알수없음"

        # 회의 전체에서 안건별 구간 추출
        agenda_contexts = extract_agendas_from_meeting(row['content'], district)

        # 안건별 GPT 분석
        for agenda_text in agenda_contexts:
            extracted_agendas = extract_info_with_gpt(agenda_text, district)
            if not extracted_agendas:
                print("  ⚠️ 해당 구간에서 안건을 찾지 못했습니다.")
                continue

            for agenda in extracted_agendas:
                processed_agenda = {
                    "안건id": f"ag{agenda_id_counter:04d}",
                    "안건명": agenda.get("안건명"),
                    "도시": "서울시",
                    "지역구": district,
                    "안건 내용 요약": agenda.get("안건 내용 요약"),
                    "관심사": agenda.get("관심사"),
                    "출처_회의명": row['title'],
                    "출처_회차": f"{row['session']} {row['sitting']}",
                    "출처_날짜": row['date'],
                    "출처_url": row['url']
                }
                final_results.append(processed_agenda)
                agenda_id_counter += 1

    print("\n\n✅ 모든 전처리 파이프라인이 완료되었습니다!")
    print(f"총 {len(final_results)}개의 안건을 추출했습니다.")

    # 예시 출력
    for result in final_results[:3]:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("-" * 20)

    save_results_to_csv(final_results, output_filepath)

# --- 스크립트 실행 ---
if __name__ == "__main__":
    csv_file_path = "nowon_short.csv"
    output_csv_path = "processed_agendas.csv"
    main_pipeline(csv_file_path, output_csv_path)
