"""
서울시 각 구의회(강동, 구로, 강서) 회의록 크롤러 공통 모듈 (POST 방식)
- 사이트별로 selector, form_data, 상세페이지 URL 생성 함수 등만 파라미터로 전달하면 재사용 가능
- 결과는 각 구별로 CSV로 저장
"""

import requests
from bs4 import BeautifulSoup
import csv, re

def crawl_post_site(
    search_url,
    form_data,
    headers,
    list_selector,             # 목록에서 각 row를 선택하는 CSS selector (예: "tbody tr")
    link_selector,             # 상세페이지 링크가 있는 a 태그의 selector (예: "td:nth-child(5) a")
    session_selector,          # 회차 정보가 있는 td selector (예: "td:nth-child(2)")
    sitting_selector,          # 차수 정보가 있는 td selector (예: "td:nth-child(4)")
    date_selector,             # 날짜 정보가 있는 td selector (예: "td:nth-child(6)")
    detail_url,                # 상세페이지 URL 
    detail_content_selector,   # 상세페이지 본문 selector (예: "div#content1")
    params_extractor,          # 상세페이지 파라미터 추출 함수 (예: lambda a: re.findall(r"'(.*?)'", a.get("onclick")))
    exclude_text="개회식",     # 제외할 텍스트(예: "개회식" 행 제외)
    result_csv="result.csv"    # 저장할 CSV 파일명
):
    """
    공통 POST 방식 크롤링 함수
    """
    # 세션 생성 및 목록 페이지 요청
    session = requests.Session()
    # 검색 페이지 불러오기 (메인 검색 페이지)
    res = session.get(search_url)
    soup = BeautifulSoup(res.text, "html.parser")
    # 1. 목록에서 정보 수집
    infos = []
    page_num = 1
    while True:
        form_data["pageIndex"] = str(page_num)
        res = session.post(search_url, data=form_data)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        found = False
        for row in soup.select(list_selector):
            a = row.select_one(link_selector)
            session_cell = row.select_one(session_selector)
            sitting = row.select_one(sitting_selector)
            date = row.select_one(date_selector)
            if a and a.get_text(strip=True) != exclude_text:
                title = a.get_text(strip=True)
                params = params_extractor(a)
                infos.append({
                    "session": session_cell.get_text(strip=True) if session_cell else "",
                    "sitting": sitting.get_text(strip=True) if sitting else "",
                    "date": date.get_text(strip=True) if date else "",
                    "title": title,
                    "params": params,
                    "content": ""  # 본문은 나중에 채움
                })
                found = True
        if not found:
            break
        page_num += 1

    # 2. 상세페이지 본문 수집
    for item in infos:
        try:
            ntime, contype, subtype, num, _, _, istemp = item["params"]
            data = {
                    "ntime": ntime,
                    "contype": contype,
                    "subtype": subtype,
                    "num": num,
                    "istemp": istemp,
                    "searchtext": ""  # 검색어 없으면 빈 문자열
                }
            detail_res = requests.post(detail_url,data=data, headers=headers)
            detail_res.raise_for_status()
            detail_soup = BeautifulSoup(detail_res.text, "html.parser")
            content = detail_soup.select_one(detail_content_selector)
            item["content"] = content.get_text(" ", strip=True) if content else ""
        except Exception as e:
            item["content"] = f"본문 수집 실패: {e}"

    # 3. CSV로 저장
    with open(result_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "params", "session", "sitting", "date", "content"])
        writer.writeheader()
        writer.writerows(infos)

# -------------------------------
# 사용 예시: 강동구, 구로구, 강서구
# -------------------------------
if __name__ == "__main__":
    # 강동구 예시 (실제 selector, form_data 등은 사이트 구조에 맞게 수정 필요)
    crawl_post_site(
        search_url="https://council.gangdong.go.kr/meeting/confer/kind.do",
        form_data = {
            "contype": "1",
            "subtype": "0",
            "series": "9",
            "pageIndex": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        list_selector="tbody tr",
        link_selector="td:nth-child(2) a",
        session_selector="td:nth-child(1)",
        sitting_selector="td:nth-child(3)",
        date_selector="td:nth-child(4)",
        detail_url="https://council.gangdong.go.kr/meeting/confer/popup.do",
        detail_content_selector="#content > div > div",
        params_extractor=lambda a: re.findall(r"'(.*?)'", a.get("onclick", "")),
        exclude_text="개회식",
        result_csv="./result/gangdong.csv"
    )

    # 구로구 예시 (실제 selector, form_data 등은 사이트 구조에 맞게 수정 필요)
    crawl_post_site(
        search_url="https://www.guroc.go.kr/meeting/confer/kind.do",
        form_data = {
            "contype": "1",
            "subtype": "0",
            "series": "9",
            "pageIndex": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        list_selector="tbody tr",
        link_selector="td:nth-child(2) a",
        session_selector="td:nth-child(1)",
        sitting_selector="td:nth-child(3)",
        date_selector="td:nth-child(4)",
        detail_url="https://www.guroc.go.kr/meeting/confer/popup.do",
        detail_content_selector="#main-content > div > div > div",
        params_extractor=lambda a: re.findall(r"'(.*?)'", a.get("onclick", "")),
        exclude_text="개회식",
        result_csv="./result/guro.csv"
    )

    # 강서구 예시 (실제 selector, form_data 등은 사이트 구조에 맞게 수정 필요)
    crawl_post_site(
        search_url="https://gsc.gangseo.seoul.kr/meeting/confer/kind.do",
        form_data = {
            "contype": "1",
            "subtype": "0",
            "series": "9",
            "pageIndex": "1",
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        list_selector="tbody tr",
        link_selector="td:nth-child(2) a",
        session_selector="td:nth-child(1)",
        sitting_selector="td:nth-child(3)",
        date_selector="td:nth-child(4)",
        detail_url="https://gsc.gangseo.seoul.kr/meeting/confer/popup.do",
        detail_content_selector="#main-content > div > div > div > div > div > div > div",
        params_extractor=lambda a: re.findall(r"'(.*?)'", a.get("onclick", "")),
        exclude_text="개회식",
        result_csv="./result/gangseo.csv"
    )
