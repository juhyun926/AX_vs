import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="무역 직무 MBTI 진단 테스트",
    page_icon="🚢",
    layout="centered"
)

# -------------------------------------------------------------
# 0. 커스텀 CSS (더 연하고 은은한 스카이블루 그라데이션 + 카드형 디자인)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 전체 배경: 화이트에 가까운 아주 연한 스카이블루 그라데이션 */
    .stApp {
        background: linear-gradient(180deg, #FAFCFF 0%, #EDF5FD 100%);
    }

    /* 상단 여백 최적화 */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* 문항 질문 박스 디자인 */
    .question-box {
        background: #FFFFFF;
        border: 1.5px solid #BAE0FD;
        border-radius: 18px;
        padding: 24px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(30, 136, 229, 0.06);
        text-align: center;
    }
    .question-title {
        color: #0369A1;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    .question-text {
        color: #1E293B;
        font-size: 1.25rem;
        font-weight: 600;
        line-height: 1.5;
        margin: 0;
        word-break: keep-all;
    }

    /* 선택지 버튼 커스텀 (둥근 카드 형태 + 부드러운 그림자) */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1.5px solid #D1E7FC !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease-in-out !important;
        text-align: left !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        height: auto !important;
    }

    /* 버튼 호버 시 효과 */
    div.stButton > button:hover {
        background-color: #F8FBFF !important;
        border-color: #38BDF8 !important;
        color: #0284C7 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(56, 189, 248, 0.18) !important;
    }

    /* 버튼 클릭 시 */
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* 결과 서브 카드 배경 스타일 */
    .result-subcard {
        background: #FFFFFF;
        border: 1px solid #D8EAFD;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(186, 224, 253, 0.2);
        margin-bottom: 20px;
    }

    /* 성향 지표 바 커스텀 카드 */
    .metric-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .metric-header {
        display: flex;
        justify-content: space-between;
        font-weight: 700;
        font-size: 0.98rem;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# 1. 20개 질문 데이터셋 정의 (각 축당 5문항)
# -------------------------------------------------------------
QUESTIONS = [
    # [E vs I] 대외협상 vs 내부조율 (1~5번)
    {
        "q": "해외 파트너와 중요한 거래 조건을 조율해야 할 때 나는?",
        "axis": ("E", "I"),
        "opt_a": "화상회의나 직접 대면 미팅으로 얼굴을 보며 적극적으로 설득한다.",
        "opt_b": "메일이나 서면으로 정돈된 공식 제안서를 주고받으며 협의한다."
    },
    {
        "q": "해외 무역 박람회 부스 운영 업무가 주어진다면?",
        "axis": ("E", "I"),
        "opt_a": "부스 밖으로 나가 지나가는 바이어에게 먼저 말을 걸고 명함을 교환한다.",
        "opt_b": "부스 안에서 상담 일지를 정리하고 카탈로그와 샘플 배치를 완벽하게 관리한다."
    },
    {
        "q": "업무 피로도가 상대적으로 덜한 하루는?",
        "axis": ("E", "I"),
        "opt_a": "하루 종일 다양한 국가의 바이어, 포워더와 쉴 새 없이 소통하고 통화한 날.",
        "opt_b": "방해받지 않고 대시보드와 선적/정산 시트를 집중해서 파고든 날."
    },
    {
        "q": "새로운 해외 판로를 개척해야 할 때 먼저 드는 생각은?",
        "axis": ("E", "I"),
        "opt_a": "'링크드인이나 현지 네트워크를 뒤져서 실무 담당자 연락처부터 뚫어보자!'",
        "opt_b": "'현지 국가 통계 보고서와 수출입 품목 데이터를 먼저 내려받아 분석해보자!'"
    },
    {
        "q": "바이어와 클레임(Claim) 분쟁이 발생했을 때 나의 대처는?",
        "axis": ("E", "I"),
        "opt_a": "즉시 통화나 미팅을 잡아 감정을 달래고 라포(Rapport)를 유지하며 푼다.",
        "opt_b": "계약서 규정과 귀책사유를 정리한 공식 레터를 작성해 논리적으로 반박한다."
    },

    # [S vs N] 규정원칙 vs 시장트렌드 (6~10번)
    {
        "q": "다음 중 업무적으로 더 흥미를 느끼는 문서는?",
        "axis": ("S", "N"),
        "opt_a": "글자 하나까지 빈틈없이 일치하는 B/L, Invoice, P/L 서류 셋과 관세청 공문.",
        "opt_b": "글로벌 소비 트렌드 리포트와 아마존/틱톡의 급상승 키워드 랭킹."
    },
    {
        "q": "수출입 품목을 검토할 때 가장 먼저 눈길이 가는 것은?",
        "axis": ("S", "N"),
        "opt_a": "정확한 HS Code 분류 가능 여부, 수입 요건 및 인허가 충족 상태.",
        "opt_b": "해외 소비자들의 바이럴 가능성, 제품 디자인의 차별성과 시장 파급력."
    },
    {
        "q": "업무 중 나를 더 스트레스 받게 만드는 상황은?",
        "axis": ("S", "N"),
        "opt_a": "서류상 오타 하나로 인해 L/C 네고 하자나 통관 지연이 생길 위험.",
        "opt_b": "경쟁사가 새로운 시장 트렌드를 먼저 선점해버려 기회를 놓칠 위험."
    },
    {
        "q": "평소 더 찾아보고 싶은 무역 뉴스는?",
        "axis": ("S", "N"),
        "opt_a": "국가별 관세율 인하, FTA 원산지 결정 기준 개정, 해상 운임 지수 동향.",
        "opt_b": "K-브랜드의 신흥 시장 진출 성공기, 크로스보더 신규 플랫폼 입점 전략."
    },
    {
        "q": "나의 업무 스타일을 비유하자면?",
        "axis": ("S", "N"),
        "opt_a": "정해진 레일 위를 탈선 없이 정확하고 안전하게 달리는 고속열차.",
        "opt_b": "파도와 바람의 흐름을 읽고 그때그때 유연하게 돛을 올리는 요트."
    },

    # [T vs F] 손익수치 vs 상황대응 (11~15번)
    {
        "q": "바이어가 무리한 단가 인하를 요구해올 때 나의 대응은?",
        "axis": ("T", "F"),
        "opt_a": "마진율 한계치와 물류비를 정밀 계산해 1원도 손해 보지 않는 선을 칼같이 긋는다.",
        "opt_b": "향후 발주 가능성과 장기적 파트너십을 고려해 일부 조건을 유연하게 맞춰준다."
    },
    {
        "q": "운송 경로(Route) 및 포워더를 선정할 때 최우선 기준은?",
        "axis": ("T", "F"),
        "opt_a": "운임 단가와 부대비용(Demurrage 등)을 수치적으로 최소화할 수 있는 견적.",
        "opt_b": "영업사원과의 오랜 신뢰 관계 및 유사시 컨테이너 스페이스를 빼줄 수 있는 협조도."
    },
    {
        "q": "업무 평가 시 더 보람을 느끼는 피드백은?",
        "axis": ("T", "F"),
        "opt_a": "'원가 마진 설계를 철저히 해서 이번 분기 영업이익률을 크게 개선하셨네요.'",
        "opt_b": "'바이어들이 담당자님과 일하는 걸 너무 좋아하네요. 고객 관리가 탁월합니다.'"
    },
    {
        "q": "서류 작업 중 통관에 큰 영향 없는 경미한 불일치를 발견했다면?",
        "axis": ("T", "F"),
        "opt_a": "원칙대로 정정 요청을 넣어 서류와 시스템상의 수치를 완벽히 일치시킨다.",
        "opt_b": "전체 선적 일정이 지연되지 않도록 유연하게 다음 절차를 진행한다."
    },
    {
        "q": "새로운 해외 공급사를 발굴할 때 결정적인 선택 기준은?",
        "axis": ("T", "F"),
        "opt_a": "투명한 원가 계산표, 공장 캐파(Capa), 재무 건전성 등 객관적 데이터.",
        "opt_b": "공장 대표 및 실무진과의 소통 케미, 비즈니스 협력에 대한 진정성."
    },

    # [J vs P] 프로세스 vs 기회포착 (16~20번)
    {
        "q": "선적 일정(Shipping Schedule)을 관리하는 나의 방식은?",
        "axis": ("J", "P"),
        "opt_a": "선적 2주 전부터 마일스톤별 체크리스트를 세우고 매일 진척도를 확인한다.",
        "opt_b": "무역은 변수가 상존하므로, 주요 이슈가 생길 때마다 즉각 순발력 있게 대응한다."
    },
    {
        "q": "출근 후 모니터에서 가장 먼저 여는 탭은?",
        "axis": ("J", "P"),
        "opt_a": "오늘 처리해야 할 일별 To-Do 리스트와 정돈된 캘린더.",
        "opt_b": "밤사이 들어온 해외 바이어/공급사의 메신저 창과 신규 알림."
    },
    {
        "q": "재고(Inventory)를 바라보는 나의 관점은?",
        "axis": ("J", "P"),
        "opt_a": "과재고는 곧 금융 비용 손실이다. 안전 재고 수준을 철저하게 통제해야 한다.",
        "opt_b": "물량이 부족해 품절되는 게 더 큰 기회손실이다. 수요가 보이면 과감히 확보해야 한다."
    },
    {
        "q": "통관 지연 등 돌발 변수가 터졌을 때 첫 행동은?",
        "axis": ("J", "P"),
        "opt_a": "표준 비상 운영 절차(SOP)를 확인하고 정해진 결재 라인에 맞춰 침착하게 대응한다.",
        "opt_b": "관세사나 물류사 담당자에게 바로 긴급 전화를 걸어 우회 루트나 예외 처리를 모색한다."
    },
    {
        "q": "이번 주 세워둔 업무 계획이 완전히 틀어졌다면?",
        "axis": ("J", "P"),
        "opt_a": "계획이 꼬였다는 사실 자체에 스트레스를 크게 받고 일정을 다시 재조정한다.",
        "opt_b": "'무역 판이 원래 그렇지' 하고 쿨하게 넘기며 즉시 차선책으로 갈아탄다."
    }
]

# -------------------------------------------------------------
# 2. 16개 MBTI -> 6개 직무 매핑
# -------------------------------------------------------------
JOB_MAPPING = {
    "ESTP": "해외영업", "ENTP": "해외영업", "ESFP": "해외영업", "ENFP": "해외영업",
    "ISTJ": "무역사무/포워딩", "ISFJ": "무역사무/포워딩", "ESTJ": "무역사무/포워딩", "ESFJ": "무역사무/포워딩",
    "ENTJ": "해외소싱/구매", "ENFJ": "해외소싱/구매",
    "INFP": "크로스보더 이커머스", "ISFP": "크로스보더 이커머스",
    "INTJ": "글로벌 SCM/물류", "INTP": "글로벌 SCM/물류", "ISTP": "글로벌 SCM/물류",
    "INFJ": "관세/컴플라이언스"
}

# -------------------------------------------------------------
# 3. 6개 무역 동물 캐릭터 (투명 누끼 SVG)
# -------------------------------------------------------------
ANIMAL_SVGS = {
    # 1. 해외영업: 쿼카 루루
    "해외영업": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="115" rx="75" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <path d="M 60,60 Q 110,80 100,30 Q 90,-10 65,30 Z" fill="#C68A4C"/>
        <g transform="translate(65, 35) rotate(12)">
          <rect x="-3" y="-35" width="22" height="15" rx="4" fill="none" stroke="#64748B" stroke-width="4"/>
          <rect x="-15" y="-20" width="45" height="60" rx="10" fill="#38BDF8"/>
          <rect x="-12" y="-17" width="39" height="54" rx="7" fill="#7DD3FC"/>
          <line x1="-15" y1="10" x2="30" y2="10" stroke="#0284C7" stroke-width="3"/>
          <circle cx="-5" cy="42" r="5" fill="#334155"/>
          <circle cx="20" cy="42" r="5" fill="#334155"/>
          <path d="M 5, -2 L 12, 5 L 8, 5 L 4, 1 L -2, 7 L -4, 5 L 0, 1 Z" fill="#FBBF24"/>
        </g>
        <ellipse cx="0" cy="55" rx="55" ry="50" fill="#D99B61"/>
        <ellipse cx="0" cy="62" rx="38" ry="36" fill="#FDEBD0"/>
        <ellipse cx="-32" cy="105" rx="16" ry="10" fill="#C68A4C"/>
        <ellipse cx="32" cy="105" rx="16" ry="10" fill="#C68A4C"/>
        <path d="M -45,35 Q -75,10 -65,-10 Q -50,-15 -40,15 Z" fill="#D99B61"/>
        <path d="M 40,40 Q 65,45 68,30 Q 55,25 35,30 Z" fill="#D99B61"/>
        <circle cx="-50" cy="-55" r="22" fill="#C68A4C"/>
        <circle cx="-50" cy="-55" r="13" fill="#F472B6" opacity="0.6"/>
        <circle cx="50" cy="-55" r="22" fill="#C68A4C"/>
        <circle cx="50" cy="-55" r="13" fill="#F472B6" opacity="0.6"/>
        <ellipse cx="0" cy="-25" rx="68" ry="60" fill="#D99B61"/>
        <ellipse cx="0" cy="-15" rx="55" ry="46" fill="#FDEBD0"/>
        <path d="M -38,-25 Q -26,-35 -14,-25" fill="none" stroke="#2D3748" stroke-width="5" stroke-linecap="round"/>
        <circle cx="26" cy="-25" r="10" fill="#2D3748"/>
        <circle cx="29" cy="-28" r="4" fill="#FFFFFF"/>
        <circle cx="23" cy="-22" r="2" fill="#FFFFFF"/>
        <ellipse cx="-35" cy="-10" rx="11" ry="6" fill="#FB7185" opacity="0.75"/>
        <ellipse cx="35" cy="-10" rx="11" ry="6" fill="#FB7185" opacity="0.75"/>
        <polygon points="0,-18 -6,-24 6,-24" fill="#4A5568"/>
        <path d="M 0,-18 Q -7,-9 -14,-14 M 0,-18 Q 7,-9 14,-14" fill="none" stroke="#4A5568" stroke-width="3" stroke-linecap="round"/>
        <g transform="translate(-72, -30) rotate(-15)">
          <rect x="0" y="0" width="18" height="25" rx="2" fill="#047857"/>
          <circle cx="9" cy="11" r="5" fill="none" stroke="#FBBF24" stroke-width="1.5"/>
          <text x="9" y="21" font-size="4" text-anchor="middle" fill="#FBBF24" font-weight="bold">PASSPORT</text>
        </g>
      </g>
    </svg>""",

    # 2. 무역사무/포워딩: 부엉이 올리
    "무역사무/포워딩": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="110" rx="65" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <ellipse cx="0" cy="40" rx="65" ry="70" fill="#6366F1"/>
        <ellipse cx="0" cy="50" rx="46" ry="50" fill="#EEF2FF"/>
        <path d="M -15,40 Q 0,48 15,40 M -20,60 Q 0,68 20,60 M -12,80 Q 0,88 12,80" fill="none" stroke="#C7D2FE" stroke-width="3" stroke-linecap="round"/>
        <ellipse cx="-25" cy="108" rx="14" ry="7" fill="#F59E0B"/>
        <ellipse cx="25" cy="108" rx="14" ry="7" fill="#F59E0B"/>
        <ellipse cx="-68" cy="40" rx="16" ry="38" fill="#4F46E5" transform="rotate(15 -68 40)"/>
        <ellipse cx="68" cy="40" rx="16" ry="38" fill="#4F46E5" transform="rotate(-20 68 40)"/>
        <g transform="translate(60, 20) rotate(-10)">
          <rect x="0" y="0" width="36" height="48" rx="3" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>
          <rect x="5" y="6" width="26" height="5" rx="1" fill="#38BDF8"/>
          <line x1="5" y1="18" x2="31" y2="18" stroke="#94A3B8" stroke-width="2"/>
          <line x1="5" y1="24" x2="25" y2="24" stroke="#94A3B8" stroke-width="2"/>
          <line x1="5" y1="30" x2="29" y2="30" stroke="#94A3B8" stroke-width="2"/>
          <circle cx="24" cy="38" r="7" fill="none" stroke="#EF4444" stroke-width="2"/>
          <text x="24" y="40" font-size="5" text-anchor="middle" fill="#EF4444" font-weight="bold">OK</text>
        </g>
        <polygon points="-45,-75 -20,-35 -55,-25" fill="#4F46E5"/>
        <polygon points="45,-75 20,-35 55,-25" fill="#4F46E5"/>
        <ellipse cx="0" cy="-20" rx="68" ry="58" fill="#6366F1"/>
        <ellipse cx="-26" cy="-20" rx="25" ry="25" fill="#FFFFFF"/>
        <ellipse cx="26" cy="-20" rx="25" ry="25" fill="#FFFFFF"/>
        <circle cx="-26" cy="-20" r="28" fill="none" stroke="#F59E0B" stroke-width="4"/>
        <circle cx="26" cy="-20" r="28" fill="none" stroke="#F59E0B" stroke-width="4"/>
        <line x1="-2" y1="-20" x2="2" y2="-20" stroke="#F59E0B" stroke-width="4"/>
        <circle cx="-24" cy="-20" r="12" fill="#1E1B4B"/>
        <circle cx="-21" cy="-24" r="5" fill="#FFFFFF"/>
        <circle cx="-26" cy="-17" r="2.5" fill="#FFFFFF"/>
        <circle cx="24" cy="-20" r="12" fill="#1E1B4B"/>
        <circle cx="27" cy="-24" r="5" fill="#FFFFFF"/>
        <circle cx="22" cy="-17" r="2.5" fill="#FFFFFF"/>
        <ellipse cx="-42" cy="-3" rx="10" ry="5" fill="#F472B6" opacity="0.8"/>
        <ellipse cx="42" cy="-3" rx="10" ry="5" fill="#F472B6" opacity="0.8"/>
        <polygon points="0,-12 -8,-3 0,5 8,-3" fill="#F59E0B"/>
      </g>
    </svg>""",

    # 3. 해외소싱/구매: 다람쥐 다미
    "해외소싱/구매": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="115" rx="75" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <path d="M 40,70 Q 125,50 115,-30 Q 105,-100 55,-70 Q 30,-50 45,10 Z" fill="#D97706"/>
        <path d="M 60,60 Q 110,40 100,-25 Q 92,-75 60,-55 Z" fill="#FDE68A"/>
        <ellipse cx="-10" cy="55" rx="55" ry="50" fill="#B45309"/>
        <ellipse cx="-10" cy="62" rx="38" ry="36" fill="#FEF3C7"/>
        <ellipse cx="-42" cy="105" rx="16" ry="10" fill="#92400E"/>
        <ellipse cx="20" cy="105" rx="16" ry="10" fill="#92400E"/>
        <circle cx="-55" cy="-55" r="18" fill="#B45309"/>
        <circle cx="-55" cy="-55" r="10" fill="#FECDD3"/>
        <circle cx="35" cy="-55" r="18" fill="#B45309"/>
        <circle cx="35" cy="-55" r="10" fill="#FECDD3"/>
        <ellipse cx="-10" cy="-20" rx="65" ry="58" fill="#B45309"/>
        <ellipse cx="-55" cy="-5" rx="20" ry="18" fill="#FDE68A"/>
        <ellipse cx="35" cy="-5" rx="20" ry="18" fill="#FDE68A"/>
        <ellipse cx="-10" cy="-10" rx="46" ry="42" fill="#FEF3C7"/>
        <circle cx="-32" cy="-22" r="9" fill="#1C1917"/>
        <circle cx="-29" cy="-25" r="3.5" fill="#FFFFFF"/>
        <circle cx="12" cy="-22" r="9" fill="#1C1917"/>
        <circle cx="15" cy="-25" r="3.5" fill="#FFFFFF"/>
        <ellipse cx="-46" cy="-2" rx="10" ry="6" fill="#F43F5E" opacity="0.8"/>
        <ellipse cx="26" cy="-2" rx="10" ry="6" fill="#F43F5E" opacity="0.8"/>
        <polygon points="-10,-14 -15,-19 -5,-19" fill="#78350F"/>
        <path d="M -10,-14 Q -15,-7 -20,-11 M -10,-14 Q -5,-7 0,-11" fill="none" stroke="#78350F" stroke-width="2.5"/>
        <rect x="-13" y="-8" width="6" height="7" rx="1" fill="#FFFFFF" stroke="#D1D5DB" stroke-width="1"/>
        <g transform="translate(45, 20) rotate(25)">
          <line x1="0" y1="0" x2="0" y2="40" stroke="#78350F" stroke-width="6" stroke-linecap="round"/>
          <circle cx="0" cy="-5" r="26" fill="#E0F2FE" opacity="0.8" stroke="#F59E0B" stroke-width="5"/>
          <path d="M -15,-15 A 20 20 0 0 1 12,-18" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>
          <circle cx="0" cy="-5" r="9" fill="#FBBF24"/>
          <text x="0" y="-2" font-size="9" text-anchor="middle" fill="#92400E" font-weight="bold">$</text>
        </g>
        <circle cx="35" cy="40" r="11" fill="#B45309"/>
      </g>
    </svg>""",

    # 4. 크로스보더 이커머스: 토끼 버니
    "크로스보더 이커머스": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="115" rx="65" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <ellipse cx="0" cy="55" rx="50" ry="46" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
        <ellipse cx="0" cy="62" rx="34" ry="32" fill="#FFF1F2"/>
        <ellipse cx="-26" cy="105" rx="14" ry="9" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
        <ellipse cx="26" cy="105" rx="14" ry="9" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
        <g transform="translate(-30, -50) rotate(-10)">
          <ellipse cx="0" cy="-45" rx="16" ry="50" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
          <ellipse cx="0" cy="-42" rx="9" ry="38" fill="#FDA4AF"/>
        </g>
        <g transform="translate(30, -50) rotate(15)">
          <ellipse cx="0" cy="-45" rx="16" ry="50" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
          <ellipse cx="0" cy="-42" rx="9" ry="38" fill="#FDA4AF"/>
        </g>
        <ellipse cx="0" cy="-15" rx="62" ry="54" fill="#FFFFFF" stroke="#F1F5F9" stroke-width="2"/>
        <ellipse cx="-24" cy="-18" rx="9" ry="11" fill="#1E293B"/>
        <circle cx="-21" cy="-22" r="4" fill="#FFFFFF"/>
        <circle cx="-26" cy="-14" r="2" fill="#FFFFFF"/>
        <ellipse cx="24" cy="-18" rx="9" ry="11" fill="#1E293B"/>
        <circle cx="27" cy="-22" r="4" fill="#FFFFFF"/>
        <circle cx="22" cy="-14" r="2" fill="#FFFFFF"/>
        <ellipse cx="-36" cy="-2" rx="12" ry="6" fill="#FB7185" opacity="0.8"/>
        <ellipse cx="36" cy="-2" rx="12" ry="6" fill="#FB7185" opacity="0.8"/>
        <polygon points="0,-9 -4,-13 4,-13" fill="#F43F5E"/>
        <path d="M 0,-9 Q -5,-3 -9,-7 M 0,-9 Q 5,-3 9,-7" fill="none" stroke="#F43F5E" stroke-width="2.5" stroke-linecap="round"/>
        <g transform="translate(42, 10) rotate(-15)">
          <rect x="0" y="0" width="26" height="46" rx="5" fill="#1E293B"/>
          <rect x="2" y="3" width="22" height="40" rx="3" fill="#EC4899"/>
          <circle cx="13" cy="20" r="7" fill="#FFFFFF"/>
          <path d="M 13,17 C 11,15 8,17 8,19 C 8,22 13,24 13,24 C 13,24 18,22 18,19 C 18,17 15,15 13,17 Z" fill="#EF4444"/>
        </g>
        <ellipse cx="40" cy="35" rx="9" ry="8" fill="#FFFFFF"/>
        <g transform="translate(-65, 30)">
          <path d="M 8,-12 Q 15,-22 22,-12" fill="none" stroke="#F59E0B" stroke-width="3"/>
          <rect x="0" y="-8" width="30" height="36" rx="4" fill="#FBBF24"/>
          <circle cx="15" cy="10" r="7" fill="none" stroke="#FFFFFF" stroke-width="2"/>
          <ellipse cx="15" cy="10" rx="3" ry="7" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
        </g>
        <ellipse cx="-42" cy="30" rx="9" ry="8" fill="#FFFFFF"/>
      </g>
    </svg>""",

    # 5. 글로벌 SCM/물류: 비버 보보
    "글로벌 SCM/물류": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="115" rx="75" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <g transform="translate(-90, 45) rotate(-25)">
          <ellipse cx="0" cy="0" rx="42" ry="24" fill="#5A3825" stroke="#3E2415" stroke-width="3"/>
          <line x1="-25" y1="-15" x2="25" y2="15" stroke="#3E2415" stroke-width="2"/>
          <line x1="-25" y1="15" x2="25" y2="-15" stroke="#3E2415" stroke-width="2"/>
        </g>
        <ellipse cx="0" cy="55" rx="55" ry="50" fill="#8D5B4C"/>
        <ellipse cx="0" cy="62" rx="38" ry="36" fill="#D7B9AA"/>
        <ellipse cx="-32" cy="105" rx="16" ry="10" fill="#5A3825"/>
        <ellipse cx="32" cy="105" rx="16" ry="10" fill="#5A3825"/>
        <g transform="translate(52, 25)">
          <rect x="0" y="0" width="46" height="58" rx="4" fill="#0284C7" stroke="#0369A1" stroke-width="2"/>
          <line x1="10" y1="4" x2="10" y2="54" stroke="#0369A1" stroke-width="3"/>
          <line x1="22" y1="4" x2="22" y2="54" stroke="#0369A1" stroke-width="3"/>
          <line x1="34" y1="4" x2="34" y2="54" stroke="#0369A1" stroke-width="3"/>
          <rect x="8" y="15" width="30" height="12" fill="#FFFFFF" rx="2"/>
          <text x="23" y="24" font-size="7" text-anchor="middle" fill="#0284C7" font-weight="bold">CBM OK</text>
        </g>
        <ellipse cx="0" cy="-20" rx="66" ry="58" fill="#8D5B4C"/>
        <ellipse cx="0" cy="-10" rx="52" ry="44" fill="#D7B9AA"/>
        <circle cx="-50" cy="-55" r="16" fill="#5A3825"/>
        <circle cx="50" cy="-55" r="16" fill="#5A3825"/>
        <ellipse cx="0" cy="-62" rx="54" ry="24" fill="#EAB308"/>
        <path d="M -54,-62 Q 0,-102 54,-62 Z" fill="#FACC15"/>
        <rect x="-10" y="-85" width="20" height="12" rx="3" fill="#EAB308"/>
        <circle cx="-24" cy="-22" r="9" fill="#1C1917"/>
        <circle cx="-21" cy="-25" r="3.5" fill="#FFFFFF"/>
        <circle cx="24" cy="-22" r="9" fill="#1C1917"/>
        <circle cx="27" cy="-25" r="3.5" fill="#FFFFFF"/>
        <ellipse cx="-38" cy="-5" rx="10" ry="5" fill="#F43F5E" opacity="0.7"/>
        <ellipse cx="38" cy="-5" rx="10" ry="5" fill="#F43F5E" opacity="0.7"/>
        <polygon points="0,-16 -7,-22 7,-22" fill="#3E2415"/>
        <path d="M 0,-16 Q -6,-9 -12,-14 M 0,-16 Q 6,-9 12,-14" fill="none" stroke="#3E2415" stroke-width="3"/>
        <rect x="-6" y="-11" width="12" height="11" rx="2" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
        <line x1="0" y1="-11" x2="0" y2="0" stroke="#CBD5E1" stroke-width="1.5"/>
        <g transform="translate(-62, 10) rotate(15)">
          <rect x="0" y="0" width="28" height="38" rx="3" fill="#CBD5E1" stroke="#94A3B8" stroke-width="2"/>
          <rect x="4" y="6" width="20" height="8" rx="1" fill="#22C55E"/>
          <circle cx="8" cy="20" r="2" fill="#64748B"/>
          <circle cx="14" cy="20" r="2" fill="#64748B"/>
          <circle cx="20" cy="20" r="2" fill="#64748B"/>
          <circle cx="8" cy="28" r="2" fill="#64748B"/>
          <circle cx="14" cy="28" r="2" fill="#64748B"/>
          <circle cx="20" cy="28" r="2" fill="#64748B"/>
        </g>
        <ellipse cx="-42" cy="36" rx="9" ry="8" fill="#8D5B4C"/>
      </g>
    </svg>""",

    # 6. 관세/컴플라이언스: 펭귄 페페
    "관세/컴플라이언스": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="240">
      <g transform="translate(150, 150)">
        <ellipse cx="0" cy="115" rx="65" ry="12" fill="#CBD5E1" opacity="0.45"/>
        <ellipse cx="0" cy="45" rx="62" ry="68" fill="#0F172A"/>
        <ellipse cx="0" cy="50" rx="42" ry="52" fill="#FFFFFF"/>
        <polygon points="0,5 -5,22 0,28 5,22" fill="#EF4444"/>
        <ellipse cx="-26" cy="110" rx="16" ry="8" fill="#F59E0B"/>
        <ellipse cx="26" cy="110" rx="16" ry="8" fill="#F59E0B"/>
        <circle cx="0" cy="-25" r="54" fill="#0F172A"/>
        <ellipse cx="-20" cy="-20" rx="20" ry="24" fill="#FFFFFF"/>
        <ellipse cx="20" cy="-20" rx="20" ry="24" fill="#FFFFFF"/>
        <circle cx="-16" cy="-22" r="8" fill="#0F172A"/>
        <circle cx="-13" cy="-25" r="3.5" fill="#FFFFFF"/>
        <circle cx="16" cy="-22" r="8" fill="#0F172A"/>
        <circle cx="19" cy="-25" r="3.5" fill="#FFFFFF"/>
        <ellipse cx="-28" cy="-5" rx="10" ry="5" fill="#F43F5E" opacity="0.75"/>
        <ellipse cx="28" cy="-5" rx="10" ry="5" fill="#F43F5E" opacity="0.75"/>
        <polygon points="0,-16 -8,-6 0,0 8,-6" fill="#F59E0B"/>
        <g transform="translate(45, 10)">
          <path d="M 0,-15 L 35,-15 C 35,20 18,38 0,46 C -18,38 -35,20 -35,-15 Z" fill="#F59E0B" stroke="#D97706" stroke-width="3"/>
          <path d="M 0,-10 L 28,-10 C 28,18 14,32 0,39 C -14,32 -28,18 -28,-10 Z" fill="#FBBF24"/>
          <path d="M 0,-2 L 3,5 L 10,5 L 5,9 L 7,16 L 0,12 L -7,16 L -5,9 L -10,5 L -3,5 Z" fill="#FFFFFF"/>
        </g>
        <g transform="translate(-68, 20) rotate(15)">
          <rect x="0" y="0" width="26" height="38" rx="3" fill="#1E3A8A"/>
          <line x1="6" y1="0" x2="6" y2="38" stroke="#FBBF24" stroke-width="2"/>
          <text x="16" y="22" font-size="7" text-anchor="middle" fill="#FBBF24" font-weight="bold">HS</text>
        </g>
      </g>
    </svg>"""
}

# -------------------------------------------------------------
# 4. 6개 직무 상세 데이터
# -------------------------------------------------------------
JOB_DETAILS = {
    "해외영업": {
        "tagline": "글로벌 시장의 최전선 돌격대장",
        "char_name": "바이어 사냥꾼 아기 쿼카 '루루' 🐾",
        "desc": "국경을 넘나들며 바이어를 발굴하고 치열한 네고를 통해 수주 계약을 성사시키는 무역의 최전방 공격수입니다.",
        "work_list": [
            "**바이어 발굴 & 인콰이어리 응대:** 해외 전시회, B2B 플랫폼, 콜드 메일을 통해 잠재 바이어를 발굴하고 견적서(Quotation)를 발송합니다.",
            "**가격 및 인코텀즈 협상:** FOB, CIF 등 거래 조건과 수량별 단가를 치열하게 밀당하며 자사 마진을 지켜내는 계약을 체결합니다.",
            "**사후 관리 & 릴레이션십 유지:** 납기 일정을 조율하고, 바이어 클레임 발생 시 발 빠르게 중재하여 지속적인 재발주(Repeat Order)를 이끌어냅니다."
        ],
        "strengths": ["글로벌 바이어 네트워킹 & 설득력", "돌발 상황을 돌파하는 순발력", "시차를 뛰어넘는 기동성"],
        "keyword": "#바이어발굴 #수주계약 #네고장인 #해외출장"
    },
    "무역사무/포워딩": {
        "tagline": "수출입 항해의 완벽한 조타수",
        "char_name": "꼼꼼 안경 아기 부엉이 '올리' 🦉",
        "desc": "선적 서류 작성부터 선박/항공 스케줄 예약, 신용장 네고까지 수출입 전 과정을 오차 없이 컨트롤하는 완벽주의자입니다.",
        "work_list": [
            "**선적 서류 셋팅 & 검토:** C/I(상업송장), P/L(포장명세서), B/L(선하증권) 등 필수 서류의 단어와 수치 오타를 0.1%도 없이 발행합니다.",
            "**운송 주선 & 스페이스 부킹:** 포워더와 선사를 조율해 화물 출항/입항 스케줄을 잡고, 컨테이너 선적 공간(Space)을 차질 없이 확보합니다.",
            "**대금 결제 & L/C 네고:** 신용장 조건과 선적 서류의 완벽한 일치를 검증하여 은행에서 하자(Discrepancy) 없이 수출 대금을 회수합니다."
        ],
        "strengths": ["오타를 용납하지 않는 디테일", "정확한 마감(Deadline) 준수", "물류 프로세스 추적 능력"],
        "keyword": "#선적서류마스터 #BL발행 #신용장네고 #포워딩조율"
    },
    "해외소싱/구매": {
        "tagline": "글로벌 가치사슬의 전략적 기획자",
        "char_name": "황금 탐지기 볼빵빵 아기 다람쥐 '다미' 🐿️",
        "desc": "전 세계 제조 공장을 샅샅이 뒤져 경쟁력 있는 제품과 원부자재를 최적의 가격에 들여오는 공급망 개척가입니다.",
        "work_list": [
            "**해외 공급선(서플라이어) 서칭:** 원가 경쟁력과 품질을 갖춘 해외 제조 공장을 리서치하고 현지 공장 실사 및 샘플 테스트를 진행합니다.",
            "**구매 단가(MOQ) 협상:** 최소 발주 수량(MOQ), 결제 조건(T/T, L/C), 납기 일정을 공급사와 유리하게 조율하여 매입 원가를 절감합니다.",
            "**공급망 안정성 및 품질 관리:** 원부자재 수급 리스크를 분산하고, 생산 공정 모니터링을 통해 불량률을 사전에 방지합니다."
        ],
        "strengths": ["시장 분석 및 원가 감각", "공급사 평가 및 협상력", "글로벌 밸류체인 설계"],
        "keyword": "#글로벌소싱 #공급사발굴 #원가절감 #바잉MD"
    },
    "크로스보더 이커머스": {
        "tagline": "국경 없는 디지털 셀링 마케터",
        "char_name": "트렌드 세터 아기 토끼 '버니' 🐰",
        "desc": "아마존, 쇼피, 틱톡샵 등 글로벌 온라인 플랫폼에서 전 세계 소비자의 지갑을 열게 만드는 디지털 무역의 승부사입니다.",
        "work_list": [
            "**글로벌 플랫폼 입점 & 리스팅:** 아마존, 쇼피 등에 최적화된 썸네일, 키워드 SEO, 상세페이지 번역/현지화 작업을 총괄합니다.",
            "**해외 퍼포먼스 마케팅:** 플랫폼 내 스폰서 광고(PPC) 운영, 틱톡/인스타그램 글로벌 인플루언서 시딩을 통해 바이럴 트래픽을 만듭니다.",
            "**해외 풀필먼트(FBA) & 리뷰 관리:** 현지 창고 재고 입출고를 관리하고, 글로벌 고객들의 별점과 리뷰 데이터를 분석해 판매 전환율을 극대화합니다."
        ],
        "strengths": ["글로벌 소비 트렌드 센스", "플랫폼 데이터 분석 및 마케팅", "민첩한 실행력"],
        "keyword": "#아마존셀러 #쇼피 #글로벌마케팅 #역직구"
    },
    "글로벌 SCM/물류": {
        "tagline": "데이터로 물류비를 깎는 전략가",
        "char_name": "스마트 안전모 아기 비버 '보보' 🦫",
        "desc": "컨테이너 적재율(CBM), 해상/항공 운임 단가, 리드타임을 숫자로 정밀 분석해 기업의 물류비를 드라마틱하게 줄여주는 최적화 전문가입니다.",
        "work_list": [
            "**물류비 시뮬레이션 & 운임 계약:** 선사별 부대비용(THC, Demurrage 등)을 수치 비교하고 입찰(Bidding)을 통해 최저 단가 운송 계약을 체결합니다.",
            "**CBM 적재율 및 운송 루트 최적화:** 제품 부피와 중량을 계산해 컨테이너 적재 효율을 극대화하고 복합운송 최단 경로를 설계합니다.",
            "**글로벌 재고 회전율 통제:** 거점 물류센터(CDC/RDC)의 안전 재고를 모니터링하여 품절 방지와 재고 비용 최소화 사이의 균형을 맞춥니다."
        ],
        "strengths": ["수리적 사고 및 데이터 분석력", "프로세스 병목 해결력", "물류 비용 최적화 감각"],
        "keyword": "#CBM계산 #물류비절감 #SCM최적화 #운임입찰"
    },
    "관세/컴플라이언스": {
        "tagline": "무역 리스크를 차단하는 원칙주의 방패",
        "char_name": "철통 황금 방패 아기 펭귄 '페페' 🐧",
        "desc": "복잡한 관세법, HS Code 분류, FTA 협정 요건을 철저히 검토해 통관 보류와 거액의 추징금 패널티를 사전에 방어하는 원칙주의 수호자입니다.",
        "work_list": [
            "**HS Code 품목분류 및 요건 확인:** 수출입 품목의 성분/용도를 분석해 정확한 세번(10자리)을 확정하고 수입 요건(인증, 검역 등)을 사전 점검합니다.",
            "**FTA 원산지 증명 관리:** BOM(원자재명세서)과 제조원가계산서를 검토해 FTA 특혜 관세 적용 요건을 판정하고 원산지증명서(C/O)를 발급/보관합니다.",
            "**수출입 통관 리스크 및 세무 방어:** 세관 통관 보류 시 신속하게 소명자료를 제출하고, 외국환거래법 및 관세 평가 적법성을 상시 점검합니다."
        ],
        "strengths": ["법령 및 규정 독해력", "원칙주의적 꼼꼼함", "수출입 리스크 차단 감각"],
        "keyword": "#HS코드 #FTA원산지 #통관리스크차단 #관세법"
    }
}

# -------------------------------------------------------------
# 5. 16개 MBTI 유형별 환상의 짝꿍
# -------------------------------------------------------------
MBTI_CHEMISTRY = {
    "ESTP": {
        "partner": "ISTJ (무역사무/포워딩)",
        "role": "브레이크 없는 스포츠카 🏎️ ❌ 절대 안 멈추는 내비게이션 🗺️",
        "reason": "ESTP가 현지 박람회에서 신나서 바이어에게 '다음 주 당장 선적 쌉가능!'을 외치며 계약서를 던져놓고 도망치면, 뒤에서 한숨을 푹 쉬며 묵묵히 서류 오타를 잡고 진짜로 배를 띄워주는 ISTJ가 있어야 회사가 망하지 않습니다."
    },
    "ENTP": {
        "partner": "INTJ (글로벌 SCM/물류)",
        "role": "아이디어 융단폭격기 💡 ❌ 팩트폭력 계산기 🧮",
        "reason": "ENTP가 '아프리카 신시장 뚫어서 이거 역수출하면 대박 각인데?'라며 화려한 썰을 풀 때, 옆에서 엑셀을 켜고 '운임비 CBM당 300불 손해라 적자입니다'라고 단칼에 팩트로 뼈를 때려주는 INTJ가 있어야 파산 신청을 피할 수 있습니다."
    },
    "ESFP": {
        "partner": "ISFJ (무역사무/포워딩)",
        "role": "인싸 세일즈 요정 🧚 ❌ 멘탈 케어 전문 수습반 🩹",
        "reason": "ESFP가 바이어랑 저녁 먹고 술 마시며 온갖 감성 소통으로 단독 수주를 따오는 동안, 서류상 인코텀즈 조건이 뭔지 까먹었을 때 조용히 다가와 '선생님, 서명만 하세요'라며 B/L을 내밀어주는 천사 ISFJ와의 궁합은 눈물겹습니다."
    },
    "ENFP": {
        "partner": "ESTJ (무역사무/포워딩)",
        "role": "자유로운 영혼의 돌격대 🦄 ❌ 규율의 헌병대장 👮",
        "reason": "ENFP가 번뜩이는 영감으로 남미 신규 바이어를 물어와 흥분해 있을 때, ESTJ가 어깨를 탁 잡고 '잠깐, 신용장 개설 확인했어? 결제 조건 T/T 선금 안 받으면 한 발짝도 선적 안 나가'라며 사기 거래를 칼같이 막아줍니다."
    },
    "ISTJ": {
        "partner": "ESTP (해외영업)",
        "role": "방구석 완벽 서류 장인 📑 ❌ 야생의 계약 사냥꾼 🏹",
        "reason": "ISTJ는 서류 작업과 통관 규정을 세상에서 제일 완벽하게 셋팅해 놨는데 정작 오더가 없으면 할 일이 없습니다. 이때 밖에서 흙탕물 튀겨가며 오더를 한 바가지 물어오는 ESTP가 있어야 당신의 완벽한 B/L이 빛을 봅니다."
    },
    "ISFJ": {
        "partner": "ENTJ (해외소싱/구매)",
        "role": "세심한 일정의 수호천사 🕊️ ❌ 불도저 야망가 🚜",
        "reason": "ENTJ가 전 세계 공장을 인수할 기세로 거대한 공급망 로드맵을 선포할 때, 뒤에서 묵묵히 통관 데드라인과 공장 출고 일정을 1분 1초 단위로 맞춰주며 ENTJ의 거대한 야망을 현실로 만들어주는 숨은 1등 공신입니다."
    },
    "ESTJ": {
        "partner": "INFP (크로스보더 이커머스)",
        "role": "원칙주의 시스템 설계자 📐 ❌ 감성 충만 트렌드 탐험가 🎨",
        "reason": "ESTJ가 짜놓은 엄격한 물류 시스템과 정산 엑셀 속에서, INFP는 해외 틱톡커들이 열광할 감성 터지는 썸네일과 상품 카피를 기가 막히게 뽑아냅니다. ESTJ의 이성과 INFP의 감성이 만나면 전 세계 완판 신화가 열립니다."
    },
    "ESFJ": {
        "partner": "ISTP (글로벌 SCM/물류)",
        "role": "오지랖 만렙 조율왕 🤝 ❌ 고독한 기술적 해결사 🛠️",
        "reason": "ESFJ가 세관 직원 및 선사 영업사원들과 호형호제하며 부드러운 라포를 형성해 두면, 물류 라인에 병목이 생겼을 때 말 한마디 없이 나타난 ISTP가 데이터를 뚝딱 만져 컨테이너 적재 최적화 알고리즘으로 화물을 탈출시킵니다."
    },
    "ENTJ": {
        "partner": "INFJ (관세/컴플라이언스)",
        "role": "대륙을 정복하는 사령관 👑 ❌ 미래를 꿰뚫는 법률 책사 📜",
        "reason": "ENTJ가 공격적인 마진 확대를 위해 신규 루트로 원자재를 싹쓸이하려고 할 때, INFJ가 조용히 뒤에서 '부장님, 그 루트로 들어오면 세관 역외탈세 조사 대상입니다'라며 감옥 갈 뻔한 보스를 구해주는 참모 역할을 해냅니다."
    },
    "ENFJ": {
        "partner": "INTP (글로벌 SCM/물류)",
        "role": "모두를 이끄는 글로벌 치어리더 📣 ❌ 골방의 데이터 천재 🧠",
        "reason": "ENFJ가 해외 공급처 대표들과 깊은 유대감을 형성해 계약 분위기를 최고조로 끌어올리면, INTP가 구석에서 조용히 복합운송 단가 모델링을 돌려 '이 조건이 최적 운임입니다'라며 이성적 방점을 찍어줍니다."
    },
    "INFP": {
        "partner": "ESTJ (무역사무/포워딩)",
        "role": "몽상하는 크리에이터 🌌 ❌ 현실 자각 타임 제조기 ⏰",
        "reason": "INFP가 '이 패키징 디자인 너무 예뻐서 해외에서 난리 날 것 같아요!'라며 꿈에 부풀어 있을 때, ESTJ가 '예쁜 건 됐고, 박스 CBM 규격 맞춰서 컨테이너에 몇 개 들어가는데?'라며 이상을 현실적인 숫자로 안착시켜 줍니다."
    },
    "ISFP": {
        "partner": "ENTP (해외영업)",
        "role": "조용한 큐레이션 장인 🖌️ ❌ 입으로 우주선 파는 세일즈맨 🚀",
        "reason": "ISFP가 조용히 모니터 뒤에서 해외 소비자들이 홀릴 만한 히트 상품을 기막힌 안목으로 찾아내 셋팅해 두면, ENTP가 그 물건을 들고 나가서 세기의 입담으로 전 세계 바이어에게 완판시키고 돌아옵니다."
    },
    "INTJ": {
        "partner": "ENFP (해외영업)",
        "role": "고독한 마스터마인드 ♟️ ❌ 텐션 폭발 에너자이저 🔋",
        "reason": "INTJ가 방구석에서 10년 치 글로벌 운임 데이터와 공급망 리스크를 완벽하게 시뮬레이션해 두면, ENFP가 그 전략을 들고 룰루랄라 해외로 날아가 바이어들의 멱살을 잡고 계약서에 도장을 찍어오는 완벽한 외유내강 팀입니다."
    },
    "INTP": {
        "partner": "ESFJ (무역사무/포워딩)",
        "role": "기계적인 엑셀 너드 🖥️ ❌ 사교계의 마당발 ☕",
        "reason": "INTP가 사람 만나기 싫어서 모니터에 머리 박고 최적 운송 루트를 수학적으로 계산하고 있을 때, ESFJ가 포워더 담당자에게 커피 기프티콘을 쏘며 선박 스페이스를 웃는 얼굴로 따와 INTP의 계획을 완성해 줍니다."
    },
    "ISTP": {
        "partner": "ESFP (해외영업)",
        "role": "침묵의 문제 해결사 🧰 ❌ 파티의 주인공 🪩",
        "reason": "해외 바이어와 술자리를 즐기던 ESFP가 현지 세관에서 화물이 묶였다며 멘붕에 빠져 전화했을 때, ISTP가 귀찮다는 듯 한숨 한 번 쉬고 10분 만에 관세사 연결해서 문제를 해결해 버리는 츤데레 콤비입니다."
    },
    "INFJ": {
        "partner": "ENTJ (해외소싱/구매)",
        "role": "원칙주의 절대 방패 🛡️ ❌ 불도저 공격수 ⚔️",
        "reason": "ENTJ의 거침없는 추진력과 INFJ의 꼼꼼한 법적 리스크 사전 차단 능력이 만나면, 법망을 합법적으로 넘나들며 최대 마진을 뽑아내는 무적의 글로벌 무역 카르텔이 완성됩니다."
    }
}

# -------------------------------------------------------------
# 6. 세션 상태 관리
# -------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = []
    st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

def reset_test():
    st.session_state.step = 0
    st.session_state.answers = []
    st.session_state.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

def go_prev():
    if st.session_state.step > 1 and st.session_state.answers:
        last_choice = st.session_state.answers.pop()
        st.session_state.scores[last_choice] -= 1
        st.session_state.step -= 1

# -------------------------------------------------------------
# 7. 화면 렌더링
# -------------------------------------------------------------

# (1) 인트로 화면
if st.session_state.step == 0:
    st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
    st.title("🚢 무역 직무 MBTI 진단")
    st.markdown("<p style='font-size: 1.2rem; color: #0284C7; font-weight: 600;'>내 성향에 딱 맞는 글로벌 무역 직무는 무엇일까?</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background: white; border-radius: 16px; padding: 22px; border: 1.5px solid #BAE0FD; box-shadow: 0 4px 14px rgba(30,136,229,0.06); margin-bottom: 25px;'>
            <p style='color: #475569; font-size: 1.05rem; margin: 0; line-height: 1.6;'>
                20개의 무역 실무 밸런스 게임을 통해 나의 무역 MBTI를 분석하고,<br>
                가장 잘 어울리는 <b>6대 핵심 무역 직무</b>와 <b>환상의 실무 파트너</b>를 찾아드립니다.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.info("⏱️ 소요 시간: 약 3분 | 총 20문항 (양자택일) | 문항 중 '뒤로가기' 가능")
    if st.button("테스트 시작하기 🚀", use_container_width=True, type="primary"):
        st.session_state.step = 1
        st.rerun()

# (2) 문항 진행 화면 (1 ~ 20번)
elif 1 <= st.session_state.step <= 20:
    current_idx = st.session_state.step - 1
    q_data = QUESTIONS[current_idx]
    
    progress = st.session_state.step / 20
    st.progress(progress, text=f"진행도: {st.session_state.step} / 20 ({int(progress * 100)}%)")
    
    # 카드형 질문 프레임
    st.markdown(
        f"""
        <div class="question-box">
            <div class="question-title">QUESTION {st.session_state.step}</div>
            <div class="question-text">{q_data['q']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # A 선택 버튼
    if st.button(f"A.  {q_data['opt_a']}", key=f"btn_a_{st.session_state.step}", use_container_width=True):
        chosen_type = q_data["axis"][0]
        st.session_state.scores[chosen_type] += 1
        st.session_state.answers.append(chosen_type)
        st.session_state.step += 1
        st.rerun()

    # B 선택 버튼
    if st.button(f"B.  {q_data['opt_b']}", key=f"btn_b_{st.session_state.step}", use_container_width=True):
        chosen_type = q_data["axis"][1]
        st.session_state.scores[chosen_type] += 1
        st.session_state.answers.append(chosen_type)
        st.session_state.step += 1
        st.rerun()

    # 이전 질문으로 돌아가기 버튼
    st.write("")
    if st.session_state.step > 1:
        if st.button("⬅️ 이전 질문으로 돌아가기 (다시 선택)", key=f"btn_prev_{st.session_state.step}"):
            go_prev()
            st.rerun()

# (3) 결과 화면 (step == 21)
else:
    scores = st.session_state.scores
    mbti = (
        ("E" if scores["E"] >= scores["I"] else "I") +
        ("S" if scores["S"] >= scores["N"] else "N") +
        ("T" if scores["T"] >= scores["F"] else "F") +
        ("J" if scores["J"] >= scores["P"] else "P")
    )
    
    matched_job = JOB_MAPPING.get(mbti, "해외영업")
    job_info = JOB_DETAILS[matched_job]
    chemistry_info = MBTI_CHEMISTRY[mbti]
    animal_svg = ANIMAL_SVGS.get(matched_job, "")

    st.balloons()

    # 상단: MBTI 코드
    st.markdown("<p style='text-align: center; color: #64748B; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 2px;'>TRADE JOB MBTI RESULT</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #0284C7; font-size: 3.4rem; font-weight: 900; margin: 0;'>{mbti}</h1>", unsafe_allow_html=True)

    # MBTI와 추천 직무 사이에 캐릭터 배치
    char_col1, char_col2, char_col3 = st.columns([1, 2.6, 1])
    with char_col2:
        st.markdown(animal_svg, unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align: center; color: #0369A1; font-weight: 700; font-size: 1rem; margin-top: -10px; margin-bottom: 12px;'>✨ {job_info['char_name']}</p>", unsafe_allow_html=True)

    # 추천 직무명 및 태그라인
    st.markdown(f"<h2 style='text-align: center; margin-top: 0; color: #0F172A; font-weight: 800;'>🎯 추천 직무: <span style='color: #0284C7;'>{matched_job}</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 1.18rem; font-style: italic; color: #64748B; margin-top: -4px;'>\"{job_info['tagline']}\"</p>", unsafe_allow_html=True)

    st.divider()

    # 1. 내 직무가 실제로 하는 일 (카드형)
    st.markdown(
        f"""
        <div class="result-subcard">
            <h3 style="color: #0F172A; margin-top: 0;">📋 내 직무가 실제로 하는 일</h3>
            <p style="color: #475569; font-size: 1.05rem; line-height: 1.6;">{job_info['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    for work in job_info["work_list"]:
        st.markdown(f"- {work}")
    
    st.write("")
    st.info(f"**대표 키워드:** {job_info['keyword']}")

    st.divider()

    # 2. 나와 잘 맞는 환상의 MBTI 궁합
    st.subheader("🤝 나와 환상의 짝꿍인 무역 MBTI는?")
    st.success(f"### Best Match: **{chemistry_info['partner']}**")
    st.markdown(f"**케미스트리 요약:** `{chemistry_info['role']}`")
    st.write("")
    st.markdown(f"**💡 왜 둘이 찰떡궁합일까?**")
    st.markdown(f"> {chemistry_info['reason']}")

    st.divider()

    # 3. [Plotly 대체] Streamlit 기본 순수 CSS/게이지 바로 성향 시각화
    st.subheader("📊 나의 4대 무역 성향 분석 지표")
    
    metrics_data = [
        ("소통 스타일", "대외협상 (E)", scores["E"], "내부조율 (I)", scores["I"]),
        ("업무 접근", "규정원칙 (S)", scores["S"], "시장트렌드 (N)", scores["N"]),
        ("판단 기준", "손익수치 (T)", scores["T"], "상황대응 (F)", scores["F"]),
        ("실행 방식", "프로세스 (J)", scores["J"], "기회포착 (P)", scores["P"]),
    ]

    for title, left_label, left_val, right_label, right_val in metrics_data:
        # 좌측 지표 기준 백분율 (총 5점)
        left_pct = int((left_val / 5.0) * 100)
        right_pct = 100 - left_pct
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">
                    <span style="color: #0284C7;">{left_label}: {left_val}점 ({left_pct}%)</span>
                    <span style="color: #64748B;">{right_label}: {right_val}점 ({right_pct}%)</span>
                </div>
                <div style="background-color: #E2E8F0; border-radius: 10px; height: 12px; width: 100%; overflow: hidden; display: flex;">
                    <div style="background-color: #0284C7; width: {left_pct}%; height: 100%;"></div>
                    <div style="background-color: #94A3B8; width: {right_pct}%; height: 100%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    if st.button("🔄 테스트 다시 하기", use_container_width=True):
        reset_test()
        st.rerun()