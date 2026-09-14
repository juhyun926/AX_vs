import streamlit as st
from src.components.country_card import render_country_card

st.set_page_config(
    page_title="글로벌 여행 가이드",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 각 페이지별 개별 함수 정의 (고유한 함수 이름 부여)
def show_korea():
    render_country_card("korea")

def show_japan():
    render_country_card("japan")

def show_china():
    render_country_card("china")

def show_usa():
    render_country_card("usa")

# 고유한 함수를 st.Page에 연결 (url_path 충돌 방지)
home_page = st.Page(
    show_korea,
    title="대한민국 (홈)",
    icon="🇰🇷",
    default=True,
    url_path="korea",
)
japan_page = st.Page(
    show_japan,
    title="일본 여행",
    icon="🇯🇵",
    url_path="japan",
)
china_page = st.Page(
    show_china,
    title="중국 여행",
    icon="🇨🇳",
    url_path="china",
)
usa_page = st.Page(
    show_usa,
    title="미국 여행",
    icon="🇺🇸",
    url_path="usa",
)

# 네비게이션 메뉴 구성
router = st.navigation(
    {
        "홈": [home_page],
        "국가별 가이드": [japan_page, china_page, usa_page],
    }
)

router.run()