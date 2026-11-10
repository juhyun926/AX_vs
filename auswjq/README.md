# 🎤 AI 면접 코치 (Streamlit)

카메라와 마이크로 실제 면접처럼 연습하면, AI가 **답변 내용 · 말하기 · 목소리 · 표정**을 분석해서 점수와 상세 리포트를 만들어 주는 면접 연습기입니다.

## 주요 기능

| # | 기능 | 구현 방식 |
|---|---|---|
| 1 | 카메라 실시간 연습 + 얼굴 인식 | MediaPipe **Face Landmarker** (웹, `@mediapipe/tasks-vision`) |
| 2 | 얼굴 표정 분석 | 52개 블렌드셰이프 → 미소 / 무표정 / 긴장 / 불안, 시선 맞춤, 눈 깜빡임, 고개 흔들림 |
| 3 | 마이크로 실제 면접처럼 연습 | 3초 카운트다운 → 녹음 → 제한 시간 자동 종료 |
| 4 | GPT 실시간 피드백 | 답변 중 일정 주기마다 중간 답변을 GPT에 보내 한 줄 코칭 표시 |
| 5 | 말하기 속도 · 논리성 · 구체성 평가 | 음절/분(SPM) 계산 + GPT의 STAR 구조·논리성·구체성·직무 적합성 채점 |
| 6 | 습관어 체크 | "음", "어", "아", "그", "um", "uh", "a" 등 횟수 · 분당 빈도 · 자막에 노란색 표시 |
| 7 | 목소리 톤 · 자신감 분석 | Web Audio로 성량, 음높이(억양 변화), 침묵, 첫 마디까지 걸린 시간 측정 |
| 8 | 맞춤형 질문 생성 | 회사/직무 입력 → **웹 검색으로 실제 기출 질문 수집** → AI 예상 질문 자동 생성 |
| 9 | 점수 + 상세 리포트 | 문항별 점수·차트, 모범 답변, 꼬리 질문, GPT 총평, Markdown/HTML/JSON 다운로드 |

> OpenAI API 키가 없어도 **표정 · 목소리 · 말하기 속도 · 습관어** 분석은 동작합니다. (GPT 평가 · 질문 생성 · 웹 검색만 꺼짐)

## 파일 구조

```
auswjq/
├── app.py                         # Streamlit 메인 앱 (3개 화면: 질문 만들기 / 실전 연습 / 리포트)
├── requirements.txt               # 파이썬 패키지 목록
├── .env                           # OpenAI API 키 (직접 입력, git 에 올라가지 않음)
├── .env.example                   # .env 예시
├── .streamlit/config.toml         # 테마(색상) · 서버 설정
├── assets/style.css               # 모던 UI 스타일 (Pretendard 폰트)
├── core/
│   ├── config.py                  # .env 로드, OpenAI 클라이언트, 공통 GPT 호출
│   ├── questions.py               # 실제 면접 질문 웹 수집 + AI 예상 질문 생성
│   ├── speech.py                  # Whisper 음성 인식, 습관어 체크, 말하기 속도
│   ├── scoring.py                 # 목소리 톤 · 자신감 · 표정 점수 규칙
│   ├── evaluator.py               # GPT 답변 평가 · 실시간 코칭 · 세션 총평
│   ├── analyzer.py                # 한 문항 분석 파이프라인 (위 모듈을 묶음)
│   └── report.py                  # Markdown / HTML / JSON 리포트
├── components/interview_recorder/ # 카메라 · 마이크 녹화 컴포넌트 (npm 빌드 불필요)
│   ├── __init__.py
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── main.js                # MediaPipe 얼굴 분석 + Web Audio + 녹음 + 실시간 자막
└── data/reports/                  # 저장한 리포트(JSON)
```

## 실행 방법

### 1. 폴더로 이동

```bash
cd auswjq
```

### 2. (선택) 가상환경 만들기

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. OpenAI API 키 설정

`.env` 파일을 열어 `OPENAI_API_KEY` 에 발급받은 키를 넣습니다. (키 발급: https://platform.openai.com/api-keys)

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_SEARCH_MODEL=gpt-4o-mini
OPENAI_STT_MODEL=whisper-1
```

`.env` 가 없다면 `.env.example` 을 복사해서 만드세요.

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

### 5. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 이 열립니다. **Chrome 또는 Edge** 를 권장합니다 (실시간 자막 기능 지원).

> ⚠️ 반드시 `auswjq` 폴더 안에서 실행해야 테마(`.streamlit/config.toml`)가 적용됩니다.

## 사용 순서

1. **① 맞춤 질문 만들기** — 회사·직무·경력(·이력서)을 입력하고
   - `🔍 실제 면접 질문 수집`: 웹 검색으로 면접 후기·기출 질문과 출처를 모읍니다.
   - `✨ AI 예상 질문 생성`: 수집한 질문과 내 이력서를 바탕으로 예상 질문을 만듭니다.
   - 표에서 연습할 질문을 체크하고 `🎬 면접 시작`.
2. **② 실전 면접 연습** — `● 답변 시작` → 카메라/마이크 권한 허용 → 3초 후 녹화 시작.
   - 오른쪽 패널에 시선·미소·성량·속도·습관어가 실시간으로 표시되고, AI 코치가 한 줄 피드백을 줍니다.
   - `■ 답변 완료`를 누르면 Whisper 음성 인식 + GPT 평가 결과가 아래에 나옵니다.
3. **③ 종합 리포트** — 역량 레이더 차트, 문항별 점수, GPT 총평·1주일 연습 계획, 리포트 다운로드.

## 점수 기준

| 항목 | 가중치 | 내용 |
|---|---|---|
| 답변 내용 | 45% | GPT 평가: 논리성 · 구체성 · 질문 의도/직무 적합성 평균 |
| 말하기 | 20% | 말하기 속도(한국어 적정 270~340 음절/분) + 습관어 빈도 |
| 목소리 | 15% | 톤(억양 변화 · 성량 안정성) + 자신감(성량 · 침묵 · 시작 속도 · 시선) |
| 표정·시선 | 20% | 시선 맞춤 · 자연스러운 미소 · 긴장 표정 · 눈 깜빡임 · 고개 흔들림 |

등급: S(90+) · A(80+) · B(70+) · C(60+) · D(50+) · F

## 배포하기 (Streamlit Community Cloud, 무료)

1. 코드를 GitHub 에 올립니다. (`.env` 는 `.gitignore` 로 제외되어 키가 올라가지 않습니다.)
2. https://share.streamlit.io 에 GitHub 계정으로 로그인 → **Create app** → **Deploy a public app from GitHub**
3. 설정
   - Repository: `juhyun926/AX_vs` · Branch: `main`
   - Main file path: `auswjq/app.py`
   - **Advanced settings** → Python version: **3.12**
4. **Advanced settings → Secrets** 에 아래 내용을 붙여넣습니다 (`.env` 대신 여기에 키를 넣어요).

   ```toml
   OPENAI_API_KEY = "sk-proj-xxxxxxxx"
   OPENAI_MODEL = "gpt-4o-mini"
   OPENAI_SEARCH_MODEL = "gpt-4o-mini"
   OPENAI_STT_MODEL = "whisper-1"
   APP_PASSWORD = "원하는-비밀번호"
   ```

5. **Deploy** → 1~3분 뒤 `https://<앱이름>.streamlit.app` 주소가 생깁니다.

> 🔒 배포 주소는 누구나 접속할 수 있으므로 `APP_PASSWORD` 를 꼭 설정하세요. 설정하지 않으면 다른 사람이 내 OpenAI 크레딧을 쓸 수 있습니다.
> 배포 주소는 https 라서 카메라·마이크가 정상 작동합니다. 코드를 수정해 GitHub 에 push 하면 자동으로 다시 배포됩니다.

## 문제 해결

- **카메라/마이크가 안 켜져요** → 주소창 왼쪽 자물쇠 아이콘에서 카메라·마이크를 *허용*으로 바꾸고 새로고침. 다른 프로그램(Zoom 등)이 카메라를 쓰고 있지 않은지 확인하세요.
- **"얼굴 분석 모델을 불러오지 못했어요"** → MediaPipe 모델을 인터넷(CDN)에서 받아옵니다. 인터넷 연결을 확인하세요.
- **실시간 자막이 안 나와요** → Chrome/Edge 에서만 지원됩니다. 자막이 없어도 녹음은 Whisper 로 분석됩니다.
- **실제 질문 수집이 "AI 지식 기반"으로 나와요** → 사용 중인 모델/계정에서 웹 검색 도구를 쓸 수 없는 경우입니다. `.env` 의 `OPENAI_SEARCH_MODEL` 을 `gpt-4o` 등 웹 검색 지원 모델로 바꿔 보세요.
- **다른 PC에서 접속하면 카메라가 안 돼요** → 브라우저는 `localhost` 또는 `https` 에서만 카메라를 허용합니다.

## 참고

- MediaPipe 웹 샘플: https://google-ai-edge.github.io/mediapipe-samples-web/#/home
- Face Landmarker 가이드: https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/web_js
- 영상은 서버로 전송·저장하지 않고 브라우저 안에서만 분석합니다. 오디오는 음성 인식을 위해 OpenAI 로 전송됩니다.
