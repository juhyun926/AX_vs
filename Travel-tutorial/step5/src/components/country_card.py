import streamlit as st

# 1. 딕셔너리 형태로 모든 국가 데이터 정의
COUNTRIES_DATA = {
    "korea": {
        "title": "🇰🇷 대한민국 (Republic of Korea)",
        "subtitle": "글로벌 여행 가이드 서비스에 오신 것을 환영합니다!",
        "image_url": "https://images.unsplash.com/photo-1538485399081-7191377e8241?auto=format&fit=crop&w=1200&q=80",
        "image_caption": "서울 경복궁",
        "info": {
            "수도": "서울특별시",
            "통화": "대한민국 원 (KRW, ₩)",
            "언어": "한국어",
            "특징": "사계절이 뚜렷하며 전통 궁궐, 현대적 도시 문화, K-컬처 및 미식의 중심지입니다.",
        },
        "links": [
            {"name": "대한민국 구석구석 (한국관광공사)", "url": "https://korean.visitkorea.or.kr"},
            {"name": "Visit Seoul 공식 사이트", "url": "https://korean.visitseoul.net"},
        ],
    },
    "japan": {
        "title": "🇯🇵 일본 (Japan)",
        "subtitle": "가까운 이웃 나라, 다채로운 매력의 일본 여행 정보",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        "image_caption": "후지산과 벚꽃 풍경",
        "info": {
            "수도": "도쿄",
            "통화": "일본 엔 (JPY, ¥)",
            "시차": "한국과 시차 없음 (UTC+9)",
            "주요 여행지": "도쿄, 오사카, 교토, 후쿠오카, 삿포로",
        },
        "links": [
            {"name": "일본 정부 관광국(JNTO) 바로가기", "url": "https://www.japan.travel/ko/kr/"}
        ],
    },
    "china": {
        "title": "🇨🇳 중국 (China)",
        "subtitle": "장엄한 대자연과 유구한 역사가 공존하는 중국 여행 정보",
        "image_url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=1200&q=80",
        "image_caption": "만리장성",
        "info": {
            "수도": "베이징",
            "통화": "위안화 (CNY, ¥)",
            "시차": "한국보다 1시간 느림 (UTC+8)",
            "주요 여행지": "베이징, 상하이, 장가계, 칭다오, 청두",
        },
        "links": [
            {"name": "중국 문화여유부 공식 사이트", "url": "https://www.mct.gov.cn/"}
        ],
    },
    "usa": {
        "title": "🇺🇸 미국 (United States of America)",
        "subtitle": "대도시의 활기와 거대한 국립공원이 맞이하는 미국 여행 정보",
        "image_url": "https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=1200&q=80",
        "image_caption": "뉴욕 맨해튼 야경",
        "info": {
            "수도": "워싱턴 D.C.",
            "통화": "미국 달러 (USD, $)",
            "입국 절차": "ESTA(전자여행허가제) 사전 신청 필수",
            "주요 여행지": "뉴욕, 로스앤젤레스, 샌프란시스코, 하와이, 그랜드 캐니언",
        },
        "links": [
            {"name": "GoUSA 미국 공식 여행 가이드", "url": "https://www.gousa.or.kr/"}
        ],
    },
}


# 2. 딕셔너리 데이터를 받아 화면을 그리는 함수
def render_country_card(country_key: str):
    data = COUNTRIES_DATA.get(country_key)
    if not data:
        st.error("해당 국가의 정보를 찾을 수 없습니다.")
        return

    st.title(data["title"])
    st.caption(data["subtitle"])

    st.image(data["image_url"], caption=data["image_caption"], use_container_width=True)
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📌 기본 정보")
        for key, value in data["info"].items():
            st.markdown(f"- **{key}**: {value}")

    with col2:
        st.subheader("🔗 공식 여행 사이트")
        for link in data["links"]:
            st.link_button(label=link["name"], url=link["url"], use_container_width=True)