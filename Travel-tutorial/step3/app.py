import streamlit as st

st.set_page_config(page_title='세계 여행 포털', page_icon='🌎')

# 영문 텍스트 대신 실제 국기 이모지 문자를 전달합니다.
home_page = st.Page('view/home.py', title='홈', icon='🏠', default=True)
usa = st.Page('view/usa.py', title='미국', icon='🇺🇸')
china = st.Page('view/china.py', title='중국', icon='🇨🇳')
japan = st.Page('view/japan.py', title='일본', icon='🇯🇵')

# 네비게이션 설정 및 실행
pg = st.navigation([home_page, usa, china, japan])
pg.run()
