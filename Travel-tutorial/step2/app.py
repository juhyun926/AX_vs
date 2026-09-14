import streamlit as st

# 페이지 설정
st.set_page_config(page_title='세계 여행 포털', page_icon='🌎')

# 사이드바 라디오 버튼 선택값을 menu 변수에 저장
menu = st.sidebar.radio('메뉴', ['홈', '미국', '중국', '일본'])

# 메뉴별 화면 구성
if menu == '홈':
    st.title('🇰🇷 대한민국')
    st.write('동아시아에 위치한 반도 국가로, 유구한 역사와 현대적인 K-컬처가 공존하는 곳입니다.')

elif menu == '미국':
    st.title('🇺🇸 미국')
    st.write('북아메리카의 연방 공화국으로, 다양한 자연경관과 세계적인 대도시들이 위치해 있습니다.')
    # 공식 관광청 링크 버튼
    st.link_button('미국 공식 관광 사이트 방문', 'https://www.visittheusa.com/')

elif menu == '중국':
    st.title('🇨🇳 중국')
    st.write('세계에서 가장 인구가 많은 지역 중 하나이자 방대한 영토와 다양한 문화유산을 보유한 국가입니다.')
    st.link_button('중국 여행 공식 사이트 방문', 'https://www.travelchina.org.cn/')

elif menu == '일본':
    st.title('🇯🇵 일본')
    st.write('동아시아의 섬나라로, 전통적인 신사와 온천, 미식 문화가 발달한 인기 여행지입니다.')
    st.link_button('일본 관광청 공식 사이트 방문', 'https://www.japan.travel/ko/kr/')