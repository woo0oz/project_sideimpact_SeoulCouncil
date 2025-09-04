"""
서울시 각 구의회(광진, 관악, 강북) 회의록 크롤러 공통 모듈
- 사이트별로 selector, base_url, 상세페이지 selector 등만 파라미터로 전달하면 재사용 가능
- GET 방식 기반
- 결과는 각 구별로 CSV로 저장
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

def crawl_get_site(
    base_url,
    search_url,
    page_selector,           # 페이지네이션에서 전체 페이지 수를 구하는 selector (예: "#pagingNav > a")
    list_selector,           # 목록에서 각 row를 선택하는 selector (예: "tbody tr")
    link_selector,           # 상세페이지 링크가 있는 a 태그 selector (예: "td:nth-child(5) a")
    session_selector,        # 회차 정보 selector (예: "td:nth-child(3)")
    sitting_selector,        # 차수 정보 selector (예: "td:nth-child(4)")
    date_selector,           # 날짜 정보 selector (예: "td:nth-child(6)")
    detail_content_selector, # 상세페이지 본문 selector (예: "div#canvas" 등)
    exclude_text="개회식",   # 제외할 텍스트(예: "개회식" 행 제외)
    result_csv="result.csv"  # 저장할 CSV 파일명
):
    """
    공통 GET 방식 크롤링 함수
    """
    infos = []
    # 1. 전체 페이지 수 구하기
    res = requests.get(search_url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    page_len = len(soup.select(page_selector))

    # 2. 목록 페이지 순회하며 정보 수집
    for page_num in range(1, page_len + 1):
        res = requests.get(search_url + str(page_num))
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for row in soup.select(list_selector):
            a = row.select_one(link_selector)
            session_cell = row.select_one(session_selector)
            sitting = row.select_one(sitting_selector)
            date = row.select_one(date_selector)
            if a and "href" in a.attrs and sitting and sitting.get_text(strip=True) != exclude_text:
                href = urljoin(base_url, a["href"])
                title = a.get_text(strip=True)
                infos.append({
                    "session": session_cell.get_text(strip=True) if session_cell else "",
                    "sitting": sitting.get_text(strip=True) if sitting else "",
                    "date": date.get_text(strip=True) if date else "",
                    "title": title,
                    "url": href,
                    "content": ""  # 본문은 나중에 채움
                })

    # 3. 상세페이지 본문 수집
    for item in infos:
        try:
            detail_res = requests.get(item["url"])
            detail_res.raise_for_status()
            detail_soup = BeautifulSoup(detail_res.text, "html.parser")
            content = detail_soup.select_one(detail_content_selector)
            item["content"] = content.get_text(" ", strip=True) if content else ""
        except Exception as e:
            item["content"] = f"본문 수집 실패: {e}"

    # 4. CSV로 저장
    with open(result_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url", "session", "sitting", "date", "content"])
        writer.writeheader()
        writer.writerows(infos)

# -------------------------------
# 사용 예시: 광진구, 관악구, 강북구
# -------------------------------
if __name__ == "__main__":
    # 광진구
    crawl_get_site(
        base_url="https://council.gwangjin.go.kr/",
        search_url="https://council.gwangjin.go.kr/kr/assembly/indexes?th_sch=9&code=A&1&keyword=&page=",
        page_selector="#pagingNav > a",
        list_selector="tbody tr",
        link_selector="td:nth-child(5) a",
        session_selector="td:nth-child(3)",
        sitting_selector="td:nth-child(4)",
        date_selector="td:nth-child(6)",
        detail_content_selector="div#canvas",
        exclude_text="개회식",
        result_csv="./result/gwangjin.csv"
    )

    # 관악구
    crawl_get_site(
        base_url="https://www.ga21c.seoul.kr/",
        search_url="https://www.ga21c.seoul.kr/kr/minutes/search.do?th_sch=9&sess_sch=all&cmt_sch=A011&page=",
        page_selector="#pagingNav > a",
        list_selector="tbody tr",
        link_selector="td:nth-child(5) a",
        session_selector="td:nth-child(3)",
        sitting_selector="td:nth-child(4)",
        date_selector="td:nth-child(6)",
        detail_content_selector="div#minutes",
        exclude_text="개회식",
        result_csv="./result/gwanak.csv"
    )

    # 강북구
    crawl_get_site(
        base_url="https://council.gangbuk.go.kr/",
        search_url="https://council.gangbuk.go.kr/kr/minutes/search.do?th_sch=9&sess_sch=all&cmt_sch=A011&page=",
        page_selector="#pagingNav > a",
        list_selector="tbody tr",
        link_selector="td:nth-child(5) a",
        session_selector="td:nth-child(3)",
        sitting_selector="td:nth-child(4)",
        date_selector="td:nth-child(6)",
        detail_content_selector="div#minutes",
        exclude_text="개회식",
        result_csv="./result/gangbuk.csv"
    )
    
    # 강남구
    crawl_get_site(
        base_url="https://www.gncouncil.go.kr/",
        search_url="https://www.gncouncil.go.kr/kr/minutes/search.do?th_sch=9&sess_sch=all&cmt_sch=A011&page=",
        page_selector="#pagingNav > a",
        list_selector="tbody tr",
        link_selector="td:nth-child(5) a",  
        session_selector="td:nth-child(3)",
        sitting_selector="td:nth-child(4)",
        date_selector="td:nth-child(6)",
        detail_content_selector="div#minutes",
        exclude_text="개회식",
        result_csv="./result/gangnam.csv"
    )