#folium으로 지도에 마커를 표시하는 예제 코드
# import folium
# 서울 시내 명소 4곳의 좌표(위도/경도)와 이름을 리스트로 받아 folium 지도를 만들고
# 각 좌표에 이름표가 붙은 마커를 찍은 다음, basic_map.html 파일로 저장하는 예제 코드입니다
# 저장된 basic_map.html 웹 브라우저로 열어서 확인
# python day6-01.py

import folium


# 서울 시내 명소 4곳 이름,위도,경도 샘플데이터
places = [
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "N서울타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "북촌한옥마을", "lat": 37.5826, "lon": 126.9835},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.5665, "lon": 127.0092},
]

# 지도의 시작 중심 좌표 (서울시청 기준) 지정해서 folium 지도 객체 생성
# 숫자가 클수록 더 가깝게 보여준다

seoul_center = [37.5665, 126.9780]
map = folium.Map(location=seoul_center, zoom_start=13)

#3 리스트에서 장소르 하나씩 꺼내며 마커추가
import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("🗺️ 서울 주요 명소 지도")

# 1. 장소 리스트 데이터 정의 (이름, 위도, 경도)
places = [
    {"name": "서울시청", "lat": 37.5665, "lon": 126.9780, "icon": "star", "color": "red"},
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770, "icon": "info-sign", "color": "blue"},
    {"name": "N서울타워", "lat": 37.5512, "lon": 126.9882, "icon": "camera", "color": "green"},
    {"name": "북촌한옥마을", "lat": 37.5826, "lon": 126.9835, "icon": "home", "color": "orange"},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.5665, "lon": 127.0092, "icon": "cloud", "color": "purple"},
]

# 2. 중심 좌표(서울시청) 기준으로 기본 지도 객체 생성
st.set_page_config(layout="wide")
center_lat = 37.5665
center_lon = 126.9780
seoul_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# 3. for 문으로 리스트를 순회하며 마커를 하나씩 지도에 추가
for place in places:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(place["name"], max_width=200),  # 클릭 시 나타나는 팝업
        tooltip=place["name"],                             # 마우스 오버 시 뜨는 툴팁
        icon=folium.Icon(color=place["color"], icon=place["icon"])
    ).add_to(seoul_map)

# 4. Streamlit 화면에 지도 렌더링
st_folium(seoul_map, use_container_width=True, height=750)