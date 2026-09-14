import os
import base64
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 파일 구조에 맞춘 상위 폴더 .env 및 fonts 경로 지정
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
parent_env_path = parent_dir / ".env"
font_path = parent_dir / "fonts" / "온글잎 콘콘체.ttf"

# .env 로드
if parent_env_path.exists():
    load_dotenv(dotenv_path=parent_env_path)
else:
    load_dotenv()

# 로컬 폰트 파일을 base64로 인코딩
def get_font_base64(path):
    if path.exists():
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

font_base64 = get_font_base64(font_path)

# 2. API 키 로드
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
if not EXCHANGE_API_KEY:
    try:
        if "EXCHANGERATE_API_KEY" in st.secrets:
            EXCHANGE_API_KEY = st.secrets["EXCHANGERATE_API_KEY"]
    except Exception:
        pass

# 페이지 기본 설정
st.set_page_config(page_title="환율계산기", page_icon="🖩", layout="centered")

# 3. CSS 설정
font_face_rule = ""
if font_base64:
    font_face_rule = f"""
    @font-face {{
        font-family: 'LocalKonkon';
        src: url('data:font/truetype;charset=utf-8;base64,{font_base64}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    """
else:
    font_face_rule = """
    @font-face {
        font-family: 'LocalKonkon';
        src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2412-1@1.0/Ownglyph_corncorn-Rg.woff2') format('woff2');
    }
    """

st.markdown(f"""
<style>
    {font_face_rule}

    .stApp {{
        background-color: #e9ecef;
    }}

    .calc-wrapper {{
        max-width: 470px;
        margin: 0 auto;
        background: linear-gradient(145deg, #2f353a, #1e2225);
        border-radius: 28px;
        padding: 26px 22px 30px 22px;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.45), inset 0 2px 4px rgba(255, 255, 255, 0.08);
        border: 4px solid #3c4248;
    }}

    .calc-top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
        padding: 0 4px;
    }}

    .calc-brand {{
        font-family: 'LocalKonkon', sans-serif !important;
        color: #000000 !important;
        background: #f1f3f5;
        padding: 6px 18px;
        border-radius: 8px;
        font-size: 28px !important;
        font-weight: bold;
        letter-spacing: 1.5px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
        display: inline-block;
    }}

    .solar-panel {{
        background: #111417;
        width: 105px;
        height: 24px;
        border-radius: 4px;
        border: 1px solid #495057;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.8);
        display: flex;
        justify-content: space-evenly;
        align-items: center;
    }}
    .solar-cell {{
        width: 20%;
        height: 80%;
        border-right: 1px solid #343a40;
        background: #1a1e21;
    }}

    /* 계산기 전자 LCD 화면: 폰트를 온글잎 콘콘체로 지정 */
    .calc-screen {{
        background: #8fa382;
        border-radius: 12px;
        padding: 16px 20px;
        border: 3px solid #55624e;
        box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.45);
        color: #000000 !important;
        text-align: left !important;
        margin-bottom: 20px;
        font-family: 'LocalKonkon', sans-serif !important;
    }}
    .lcd-sub {{
        font-family: 'LocalKonkon', sans-serif !important;
        font-size: 16px;
        font-weight: bold;
        color: #000000 !important;
        margin-bottom: 6px;
        text-align: left !important;
    }}
    .lcd-main {{
        font-family: 'LocalKonkon', sans-serif !important;
        font-size: 38px;
        font-weight: 900;
        color: #000000 !important;
        letter-spacing: 1px;
        line-height: 1.2;
        text-align: left !important;
    }}

    /* 라벨(TO, FROM, 입력 금액 등) 네모 박스 제거 및 순수 검정 텍스트 적용 */
    .stSelectbox label, 
    .stNumberInput label, 
    label[data-testid="stWidgetLabel"] p {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 4px !important;
        color: #ffffff !important; /* 계산기 본체 어두운 배경 대비 가독성 확보 */
        font-weight: 800 !important;
        font-size: 15px !important;
        display: block !important;
    }}

    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: #ffffff !important;
        border-radius: 8px !important;
        border: 2px solid #adb5bd !important;
    }}
    input {{
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }}
    div[data-baseweb="select"] span {{
        color: #000000 !important;
        font-weight: bold !important;
    }}

    /* 계산기 키패드 */
    .keypad-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 20px;
        padding-top: 18px;
        border-top: 2px solid #3c4248;
    }}

    .calc-btn {{
        background: linear-gradient(145deg, #444b52, #32373c);
        color: #ffffff;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 20px;
        font-weight: bold;
        height: 52px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 12px;
        box-shadow: 0 4px 0 #1c2023, 0 6px 10px rgba(0,0,0,0.4);
        user-select: none;
        cursor: pointer;
        transition: all 0.08s ease;
    }}
    .calc-btn:hover {{
        background: linear-gradient(145deg, #4e555d, #393f44);
    }}
    .calc-btn:active {{
        transform: translateY(3px);
        box-shadow: 0 1px 0 #1c2023, 0 2px 4px rgba(0,0,0,0.3);
    }}

    .calc-btn-danger {{
        background: linear-gradient(145deg, #d9383a, #b32426) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 0 #731315, 0 6px 10px rgba(0,0,0,0.4) !important;
    }}
    .calc-btn-danger:hover {{
        background: linear-gradient(145deg, #e3484a, #c02b2d) !important;
    }}
    .calc-btn-danger:active {{
        transform: translateY(3px);
        box-shadow: 0 1px 0 #731315 !important;
    }}

    .calc-btn-op {{
        background: linear-gradient(145deg, #4a5560, #38424b) !important;
        color: #ffd166 !important;
        box-shadow: 0 4px 0 #21282e, 0 6px 10px rgba(0,0,0,0.4) !important;
    }}
    .calc-btn-op:hover {{
        background: linear-gradient(145deg, #566370, #424e58) !important;
    }}
    .calc-btn-op:active {{
        transform: translateY(3px);
        box-shadow: 0 1px 0 #21282e !important;
    }}

    .calc-btn-equal {{
        background: linear-gradient(145deg, #06d6a0, #04a57b) !important;
        color: #0b3d30 !important;
        box-shadow: 0 4px 0 #02664c, 0 6px 10px rgba(0,0,0,0.4) !important;
    }}
    .calc-btn-equal:hover {{
        background: linear-gradient(145deg, #1be0ab, #05b889) !important;
    }}
    .calc-btn-equal:active {{
        transform: translateY(3px);
        box-shadow: 0 1px 0 #02664c !important;
    }}

    div.stButton > button {{
        background: linear-gradient(145deg, #495057, #343a40) !important;
        color: #f8f9fa !important;
        border: 1px solid #6c757d !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 0 #212529 !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. 환율 데이터 가져오기 (1시간 캐시)
@st.cache_data(ttl=3600)
def fetch_rates(base_currency, api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if res.status_code == 200 and data.get("result") == "success":
            return data["conversion_rates"]
        return None
    except Exception:
        return None

CURRENCY_DICT = {
    "KRW": "KRW (대한민국 원)",
    "USD": "USD (미국 달러)",
    "JPY": "JPY (일본 엔)",
    "EUR": "EUR (유로)",
    "CNY": "CNY (중국 위안)",
    "GBP": "GBP (영국 파운드)",
    "VND": "VND (베트남 동)",
    "THB": "THB (태국 바트)"
}

if "from_curr" not in st.session_state:
    st.session_state.from_curr = "USD"
if "to_curr" not in st.session_state:
    st.session_state.to_curr = "KRW"

def swap():
    st.session_state.from_curr, st.session_state.to_curr = st.session_state.to_curr, st.session_state.from_curr

# ----------------- 계산기 본체 -----------------
st.markdown("""
<div class="calc-wrapper">
<div class="calc-top-bar">
<span class="calc-brand">환율계산기</span>
<div class="solar-panel">
<div class="solar-cell"></div>
<div class="solar-cell"></div>
<div class="solar-cell"></div>
<div class="solar-cell"></div>
</div>
</div>
""", unsafe_allow_html=True)

if not EXCHANGE_API_KEY:
    st.error("API 키를 찾을 수 없습니다. 상위 폴더의 `.env` 파일을 확인해주세요.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 통화 선택 UI
curr_keys = list(CURRENCY_DICT.keys())
c1, c_swap, c2 = st.columns([5, 2, 5])

with c1:
    from_curr = st.selectbox(
        "FROM",
        options=curr_keys,
        format_func=lambda x: CURRENCY_DICT.get(x, x),
        key="from_curr"
    )

with c_swap:
    st.write("")
    st.write("")
    st.button("⇄", on_click=swap, help="통화 맞바꾸기", use_container_width=True)

with c2:
    to_curr = st.selectbox(
        "TO",
        options=curr_keys,
        format_func=lambda x: CURRENCY_DICT.get(x, x),
        key="to_curr"
    )

# 금액 입력
amount = st.number_input(
    f"입력 금액 ({from_curr})",
    min_value=0.0,
    value=1.0 if from_curr != "KRW" else 10000.0,
    step=10.0 if from_curr != "KRW" else 1000.0
)

# 환율 계산 로직
rates = fetch_rates(from_curr, EXCHANGE_API_KEY)

if rates and to_curr in rates:
    rate = rates[to_curr]
    converted_val = amount * rate
    display_text = f"{converted_val:,.2f}"
    rate_info = f"1 {from_curr} = {rate:,.4f} {to_curr}"
else:
    display_text = "ERROR"
    rate_info = "NETWORK / API ERROR"

# 1. LCD 화면 (온글잎 콘콘체 적용)
st.markdown(f"""
<div class="calc-screen">
<div class="lcd-sub">{rate_info}</div>
<div class="lcd-main">{display_text} <span style="font-size:22px;">{to_curr}</span></div>
</div>
""", unsafe_allow_html=True)

# 2. 숫자 및 연산자 키패드
st.markdown("""<div class="keypad-grid">
<div class="calc-btn calc-btn-danger">AC</div>
<div class="calc-btn calc-btn-danger">C</div>
<div class="calc-btn calc-btn-op">+/-</div>
<div class="calc-btn calc-btn-op">÷</div>
<div class="calc-btn">7</div>
<div class="calc-btn">8</div>
<div class="calc-btn">9</div>
<div class="calc-btn calc-btn-op">×</div>
<div class="calc-btn">4</div>
<div class="calc-btn">5</div>
<div class="calc-btn">6</div>
<div class="calc-btn calc-btn-op">-</div>
<div class="calc-btn">1</div>
<div class="calc-btn">2</div>
<div class="calc-btn">3</div>
<div class="calc-btn calc-btn-op">+</div>
<div class="calc-btn">0</div>
<div class="calc-btn">00</div>
<div class="calc-btn">.</div>
<div class="calc-btn calc-btn-equal">=</div>
</div>""", unsafe_allow_html=True)

# 계산기 본체 닫기
st.markdown("</div>", unsafe_allow_html=True)