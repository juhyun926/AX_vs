import os
import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

st.set_page_config(
    page_title="Voyage Mate | Global Travel Assistant",
    page_icon="🫧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. 감성 버터-파스텔 테마 및 커스텀 스타일링
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 전체 배경: 따뜻하고 부드러운 크림 버터 톤 */
    .stApp {
        background: #FFFDF2;
        font-family: 'Pretendard', sans-serif;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #FFF9E6 !important;
        border-right: 2px solid #F6E7B8 !important;
    }

    /* 상단 배너 & 빅 타이틀 */
    .cute-banner {
        background: #FFFFFF;
        border: 2.5px solid #FFE066;
        border-radius: 26px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 8px 26px rgba(255, 224, 102, 0.32);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .cute-banner h1 {
        color: #1F2937;
        font-size: 38px !important;
        font-weight: 900 !important;
        margin: 6px 0 2px 0;
        letter-spacing: -1px;
        line-height: 1.2;
    }
    .cute-badge {
        background-color: #3B82F6;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 999px;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
    }

    /* 연파랑 스팟 카드 */
    .cute-card {
        background-color: #F0F7FF;
        border: none !important;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.05);
        transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .cute-card:hover {
        background-color: #E6F1FE;
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.12);
    }
    .cute-card-badge {
        background: #FFFFFF;
        color: #2563EB;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
        display: inline-block;
        margin-bottom: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .cute-card-title {
        font-size: 17px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .cute-card-desc {
        font-size: 13px;
        color: #475569;
        margin: 3px 0;
        line-height: 1.45;
    }

    /* 사이드바 통화 강조 칩 */
    .curr-highlight {
        background: #FFFFFF;
        border: 2px dashed #3B82F6;
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 14px;
        text-align: center;
    }

    /* ✨ 환율 결과 알림 박스를 파스텔 블루로 변경 */
    div[data-testid="stAlert"] {
        background-color: #F0F7FF !important;
        color: #1D4ED8 !important;
        border: 1.5px solid #BFDBFE !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.06) !important;
    }
    div[data-testid="stAlert"] p {
        color: #1D4ED8 !important;
        font-weight: 700 !important;
    }

    /* 메인 검색 버튼 */
    div.stButton > button {
        background: #FEE500 !important;
        color: #1F2937 !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 14px !important;
        height: 44px;
        box-shadow: 0 4px 12px rgba(254, 229, 0, 0.45) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: #3B82F6 !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35) !important;
        transform: translateY(-1px);
    }

    /* 추천 태그 칩 */
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        background-color: #FFFFFF !important;
        color: #4B5563 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        height: 38px !important;
        border-radius: 999px !important;
        border: 1.5px solid #F1E2A8 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background-color: #FFE066 !important;
        color: #1F2937 !important;
        border-color: #FFE066 !important;
    }

    /* 구글 지도 링크 버튼 */
    div[data-testid="stLinkButton"] > a {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        border: 1.5px solid #DCEBFE !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        border-radius: 12px !important;
        text-align: center;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.04) !important;
        transition: all 0.2s;
    }
    div[data-testid="stLinkButton"] > a:hover {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }
</style>
""", unsafe_allow_html=True)


# 2. 국가 코드 <-> 통화 매핑 딕셔너리
COUNTRY_TO_CURRENCY = {
    "jp": "JPY",  # 일본
    "us": "USD",  # 미국
    "fr": "EUR", "de": "EUR", "it": "EUR", "es": "EUR", "nl": "EUR", "at": "EUR", "be": "EUR", "pt": "EUR",  # 유럽
    "gb": "GBP",  # 영국
    "cn": "CNY",  # 중국
    "th": "THB",  # 태국
    "vn": "VND",  # 베트남
    "tw": "TWD",  # 대만
    "ch": "CHF",  # 스위스
    "au": "AUD",  # 호주
    "ca": "CAD",  # 캐나다
    "sg": "SGD",  # 싱가포르
    "ph": "PHP",  # 필리핀
    "kr": "KRW",  # 한국
}

CURRENCY_INFO = {
    "JPY": {"name": "일본 엔 (JPY)", "symbol": "¥"},
    "USD": {"name": "미국 달러 (USD)", "symbol": "$"},
    "EUR": {"name": "유럽 유로 (EUR)", "symbol": "€"},
    "GBP": {"name": "영국 파운드 (GBP)", "symbol": "£"},
    "CNY": {"name": "중국 위안 (CNY)", "symbol": "¥"},
    "THB": {"name": "태국 바트 (THB)", "symbol": "฿"},
    "VND": {"name": "베트남 동 (VND)", "symbol": "₫"},
    "TWD": {"name": "대만 달러 (TWD)", "symbol": "NT$"},
    "CHF": {"name": "스위스 프랑 (CHF)", "symbol": "CHF"},
    "AUD": {"name": "호주 달러 (AUD)", "symbol": "A$"},
    "CAD": {"name": "캐나다 달러 (CAD)", "symbol": "C$"},
    "SGD": {"name": "싱가포르 달러 (SGD)", "symbol": "S$"},
    "PHP": {"name": "필리핀 페소 (PHP)", "symbol": "₱"},
    "KRW": {"name": "대한민국 원 (KRW)", "symbol": "₩"},
}


# 3. 글로벌 장소 검색 함수
@st.cache_data(ttl=3600)
def search_global_places(query: str, limit: int = 8):
    if not query.strip():
        return []
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": limit,
        "accept-language": "ko,en",
    }
    headers = {"User-Agent": "VoyageMateApp/1.0 (streamlit-travel-service)"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception:
        return []


# 4. 실시간 환율 조회 함수
@st.cache_data(ttl=3600)
def get_exchange_rate(target_currency: str):
    if target_currency == "KRW":
        return 1.0
    if not EXCHANGERATE_API_KEY:
        return None
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/{target_currency}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json().get("conversion_rates", {}).get("KRW")
        return None
    except Exception:
        return None


# 세션 상태 초기화
if "active_global_query" not in st.session_state:
    st.session_state["active_global_query"] = "도쿄 타워"
if "auto_currency" not in st.session_state:
    st.session_state["auto_currency"] = "JPY"


# 5. 상단 브랜드 배너
st.markdown("""
<div class="cute-banner">
    <div>
        <span class="cute-badge">✦ GLOBAL TRIP COMPANION ✦</span>
        <h1> 🐹Voyage Mate : Global Travel Assistant</h1>
        <p style="margin: 6px 0 0 0; color: #64748B; font-size: 14px; font-weight: 500;">
            목적지를 검색하면 지도 이동과 함께 현지 통화 환율이 자동으로 쏙 바뀝니다!
        </p>
    </div>
    <div style="font-size: 50px; margin-left: 20px;">🎒✈️</div>
</div>
""", unsafe_allow_html=True)


# 6. 검색창 & 추천 칩
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "전 세계 목적지 검색창",
        value=st.session_state["active_global_query"],
        placeholder="어디로 훌쩍 떠나볼까요? (예: 도쿄 긴자, 파리 몽마르트르, 뉴욕 브루클린, 방콕 짜뚜짝)",
        label_visibility="collapsed",
    )
with col_btn:
    if st.button("스팟 탐색 ✨", use_container_width=True):
        st.session_state["active_global_query"] = user_input
        st.rerun()

tag_list = ["도쿄 타워 🇯🇵", "파리 에펠탑 🇫🇷", "뉴욕 타임스퀘어 🇺🇸", "방콕 카오산로드 🇹🇭", "로마 콜로세움 🇮🇹", "런던 빅벤 🇬🇧"]
tag_cols = st.columns(len(tag_list))
for idx, tag in enumerate(tag_list):
    clean_tag = tag.split()[0] + " " + tag.split()[1] if len(tag.split()) > 1 else tag
    if tag_cols[idx].button(tag, use_container_width=True):
        st.session_state["active_global_query"] = clean_tag
        st.rerun()

st.write("")


# 7. 장소 검색 및 국가 자동 감지
query_to_run = st.session_state["active_global_query"]
places = search_global_places(query_to_run, limit=8)

detected_currency = "USD"
detected_country_name = "해외"

if places:
    first_place = places[0]
    address_info = first_place.get("address", {})
    country_code = address_info.get("country_code", "").lower()
    detected_country_name = address_info.get("country", "선택된 여행지")

    if country_code in COUNTRY_TO_CURRENCY:
        detected_currency = COUNTRY_TO_CURRENCY[country_code]
        st.session_state["auto_currency"] = detected_currency


# 8. 사이드바 (자동 환율 계산기 + 체크리스트)
with st.sidebar:
    st.markdown("## 🧭 여행 플래너 포켓")
    st.caption("검색 지역에 맞춰 환율이 자동으로 세팅돼요.")
    st.divider()

    st.markdown(f"""
    <div class="curr-highlight">
        <div style="font-size: 11.5px; font-weight: 700; color: #2563EB;">📍 현재 감지된 여행지</div>
        <div style="font-size: 16px; font-weight: 800; color: #1E293B; margin-top: 2px;">{detected_country_name}</div>
        <div style="font-size: 12px; color: #64748B; margin-top: 2px;">연동 통화: <b>{st.session_state['auto_currency']}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💱 실시간 현지 환율")
    
    curr_keys = list(CURRENCY_INFO.keys())
    curr_index = curr_keys.index(st.session_state["auto_currency"]) if st.session_state["auto_currency"] in curr_keys else 0
    selected_curr = st.selectbox(
        "조회 통화 (자동 선택됨)",
        curr_keys,
        index=curr_index,
        format_func=lambda x: CURRENCY_INFO[x]["name"]
    )
    
    c_symbol = CURRENCY_INFO[selected_curr]["symbol"]

    if selected_curr == "KRW":
        st.info("💡 국내(원화) 모드입니다.")
    else:
        rate = get_exchange_rate(selected_curr)
        if rate:
            st.metric(label=f"1 {selected_curr} 기준", value=f"{rate:,.2f} 원")
            
            calc_val = st.number_input(
                f"금액 환산 ({c_symbol})",
                min_value=1.0,
                value=100.0,
                step=10.0,
                key="cute_calc_val"
            )
            total_krw = calc_val * rate
            # ✨ 파스텔 블루 알림창으로 출력
            st.success(f"약 **{total_krw:,.0f} KRW**")
        else:
            st.warning("환율 키를 확인해주세요.")

    st.divider()

    st.markdown("### 🎒 잊지마요! 여행 챙김이")
    st.checkbox("여권 유효기간 6개월 이상 남았나요?", value=True)
    st.checkbox(f"{detected_country_name} 입국 비자 / eTA 사전 체크")
    st.checkbox("해외 결제 수수료 무료 카드 충전")
    st.checkbox("현지 eSIM / 와이파이 도시락 예약")
    st.checkbox("멀티 어댑터 돼지코 & 보조배터리")
    st.checkbox("상비약 (소화제/진통제/지사제) 챙기기")


# 9. 2분할 뷰 (좌측: 지도 / 우측: 스팟 카드 목록)
if places:
    col_left_map, col_right_list = st.columns([1.15, 0.85], gap="large")

    with col_left_map:
        st.markdown(f"### 🗺️ '{query_to_run}' 주변 지도")
        map_points = [
            {
                "lat": float(p["lat"]),
                "lon": float(p["lon"]),
                "name": p.get("display_name", "").split(",")[0],
            }
            for p in places
        ]
        st.map(pd.DataFrame(map_points), latitude="lat", longitude="lon", zoom=12, size=35)

    with col_right_list:
        st.markdown(f"### 📍 스팟 리스트 ({len(places)}곳)")
        
        with st.container(height=540):
            for idx, p in enumerate(places):
                display_parts = p.get("display_name", "").split(",")
                place_title = display_parts[0].strip() if display_parts else "글로벌 명소"
                place_address = ", ".join([part.strip() for part in display_parts[1:3]]) if len(display_parts) > 1 else p.get("display_name", "상세 위치")
                
                cat = p.get("type", "스팟").capitalize()
                lat = p.get("lat")
                lon = p.get("lon")
                google_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                st.markdown(f"""
                <div class="cute-card">
                    <span class="cute-card-badge">✨ {cat}</span>
                    <div class="cute-card-title">{idx + 1}. {place_title}</div>
                    <div class="cute-card-desc">📍 {place_address}</div>
                    <div class="cute-card-desc" style="font-size: 11.5px; color: #64748B;">🌐 {float(lat):.4f}, {float(lon):.4f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.link_button("구글 지도로 길찾기 ↗", url=google_url, use_container_width=True)
                st.write("")
else:
    st.info("검색된 해외 명소 결과가 없습니다. 다른 도시나 영문(예: Tokyo, Paris)으로 검색해보세요!")