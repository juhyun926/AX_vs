#날씨 API 실습
#Open WeatherMap 현재 날씨 API 로 특정 도시의 날씨를 가져와 출력한다
#사전준비 openweatherMap 회원 가입후 ApI 발급
# pip install requests python-dotenv
#.env파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은 _API_키(깃에 안올려)
#.env.example OPENWEATHER_API_KEY=your_key
#.env.example 받아서 .env로 이름 바꾸고 자기 API를 채운다


# from dotenv import load_dotenv

# load_dotenv() #.env 파일을 읽어 환경변수로 등록한다.

# API_KEY = os.getenv('OPENWEATHER_API_KEY') #api키 OPENWEATHER_API_KEY에 직접 언급하면 안돼


import os
import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv

# 상위 디렉터리 .env 자동 로드
load_dotenv(find_dotenv())

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# 와이드 모드로 설정하여 좌우 배치가 시원하게 보이도록 구성
st.set_page_config(page_title="글로벌 날씨 & 실시간 환율 대시보드", page_icon="🌐", layout="wide")

st.title("🌐 글로벌 날씨 & 실시간 환율 대시보드")
st.caption("OpenWeatherMap & ExchangeRate-API 실시간 데이터 연동")

# API 키 유효성 체크
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    st.error("API 키를 확인해주세요. `.env` 파일에 `OPENWEATHER_API_KEY`와 `EXCHANGERATE_API_KEY`가 모두 필요합니다.")
    st.stop()

# 화면 분할: 왼쪽(날씨) / 오른쪽(환율)
left_col, right_col = st.columns([1, 1], gap="large")

# ==========================================
# [LEFT COLUMN] 실시간 날씨 섹션
# ==========================================
with left_col:
    st.subheader("🌤️ 실시간 날씨 정보")
    
    with st.form("weather_form"):
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            city_name = st.text_input("도시 이름 (영문)", value="Seoul", placeholder="예: Seoul, Tokyo, New York")
        with col_btn:
            st.write("")
            st.write("")
            weather_submitted = st.form_submit_button("날씨 조회", use_container_width=True)

    if city_name.strip():
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "q": city_name.strip(),
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "kr"
        }

        try:
            w_res = requests.get(weather_url, params=weather_params, timeout=5)
            w_data = w_res.json()

            if w_res.status_code == 200:
                weather_desc = w_data["weather"][0]["description"]
                icon_code = w_data["weather"][0]["icon"]
                temp = w_data["main"]["temp"]
                feels_like = w_data["main"]["feels_like"]
                humidity = w_data["main"]["humidity"]
                wind_speed = w_data["wind"]["speed"]
                country = w_data["sys"]["country"]

                st.success(f"**{w_data['name']} ({country})** 날씨 결과")
                
                c_icon, c_temp = st.columns([1, 2])
                with c_icon:
                    st.image(f"https://openweathermap.org/img/wn/{icon_code}@4x.png", width=110)
                with c_temp:
                    st.metric(label="현재 기온", value=f"{temp:.1f} °C", delta=f"체감 {feels_like:.1f} °C")
                    st.write(f"상태: **{weather_desc}**")

                st.divider()
                sub_col1, sub_col2 = st.columns(2)
                sub_col1.metric("습도", f"{humidity}%")
                sub_col2.metric("풍속", f"{wind_speed} m/s")

            elif w_res.status_code == 404:
                st.warning("입력하신 도시를 찾을 수 없습니다. 영문 철자를 확인해주세요.")
            else:
                st.error(f"날씨 조회 실패: {w_data.get('message', '오류 발생')}")
        except requests.exceptions.RequestException as e:
            st.error(f"날씨 API 호출 에러: {e}")

# ==========================================
# [RIGHT COLUMN] 실시간 환율 섹션
# ==========================================
with right_col:
    st.subheader("💱 실시간 환율 정보 (USD 기준)")

    # ExchangeRate-API 최신 환율 가져오기
    exchange_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"

    try:
        ex_res = requests.get(exchange_url, timeout=5)
        ex_data = ex_res.json()

        if ex_res.status_code == 200 and ex_data.get("result") == "success":
            rates = ex_data["conversion_rates"]
            krw_rate = rates.get("KRW", 0)
            jpy_rate = rates.get("JPY", 0)
            eur_rate = rates.get("EUR", 0)
            cny_rate = rates.get("CNY", 0)

            # 주요 통화 대시보드 카드
            r_col1, r_col2 = st.columns(2)
            r_col1.metric("USD / KRW", f"{krw_rate:,.2f} 원")
            r_col2.metric("USD / JPY", f"{jpy_rate:,.2f} 엔")

            r_col3, r_col4 = st.columns(2)
            r_col3.metric("USD / EUR", f"{eur_rate:,.4f} 유로")
            r_col4.metric("USD / CNY", f"{cny_rate:,.4f} 위안")

            st.divider()
            
            # 실시간 통화 계산기
            st.markdown("##### 🔢 실시간 통화 계산기")
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                target_currency = st.selectbox(
                    "변환할 통화",
                    options=["KRW", "JPY", "EUR", "CNY", "GBP", "CAD", "AUD"],
                    index=0
                )
            with calc_col2:
                usd_amount = st.number_input("달러 금액 ($)", min_value=1.0, value=100.0, step=10.0)

            converted_val = usd_amount * rates.get(target_currency, 0)
            st.info(f"**${usd_amount:,.2f} USD** = **{converted_val:,.2f} {target_currency}**")

        else:
            st.error(f"환율 데이터를 가져올 수 없습니다: {ex_data.get('error-type', '알 수 없는 에러')}")

    except requests.exceptions.RequestException as e:
        st.error(f"환율 API 호출 에러: {e}")