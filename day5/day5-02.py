#대화 기록을 기억하는 멀티턴 챗봇(스트리밍 응답)
#st.session 에 대화 기옥을 저장해서 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 streamlit의 채팅 전용 위젯을 사용합니다
# stream=True 옵션으로 답변이 실시간으로 타이핑되듯 출력됩니다
# streamlit run day5-02.py

#시스템 메시지를 사용자가 설정하도록
#대화 기록 초기화 버튼



# import streamlit as st
# from openai import OpenAI

# # 페이지 기본 설정
# st.set_page_config(page_title="멀티턴 스트리밍 챗봇", page_icon="💬", layout="wide")
# st.title("💬 나의 멀티턴 챗봇")
# st.caption("대화 기록을 기억하고 실시간 스트리밍으로 응답하는 챗봇입니다.")

# # ----------------- 사이드바 설정 -----------------
# with st.sidebar:
#     st.header("⚙️ 설정")
#     api_key = st.text_input("OpenAI API Key", type="password", help="sk-... 형태의 키를 입력하세요.")
#     model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"], index=0)
    
#     st.divider()
    
#     # 시스템 프롬프트(챗봇 역할/페르소나) 사용자 지정
#     system_instruction = st.text_area(
#         "시스템 메시지 (챗봇의 성격/역할)",
#         value="당신은 친절하고 전문적인 AI 비서입니다. 명확하고 간결하게 답변해주세요.",
#         height=120
#     )
    
#     # 대화 기록 초기화 버튼
#     if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
#         st.session_state.messages = []
#         st.rerun()

#     st.markdown("[OpenAI API 키 발급받기](https://platform.openai.com/api-keys)")

# # ----------------- 대화 기록 세션 초기화 -----------------
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # ----------------- 이전 대화 내용 출력 -----------------
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ----------------- 사용자 입력 및 응답 처리 -----------------
# if prompt := st.chat_input("메시지를 입력하세요..."):
#     # 1. API 키 입력 여부 검증
#     if not api_key:
#         st.error("오른쪽 또는 왼쪽 사이드바에서 OpenAI API Key를 먼저 입력해주세요.")
#         st.stop()

#     # 2. 사용자 메시지 세션에 추가 및 화면 출력
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 3. 모델에 전달할 전체 메시지 목록 구성 (시스템 메시지 + 이전 대화 기록)
#     api_messages = [{"role": "system", "content": system_instruction}] + st.session_state.messages

#     # 4. OpenAI API 호출 및 스트리밍 출력
#     client = OpenAI(api_key=api_key)
    
#     with st.chat_message("assistant"):
#         try:
#             stream = client.chat.completions.create(
#                 model=model,
#                 messages=api_messages,
#                 stream=True  # 실시간 스트리밍 활성화
#             )
#             # st.write_stream은 제너레이터를 받아 한 글자씩 출력하고 전체 텍스트를 반환합니다.
#             response_content = st.write_stream(stream)
            
#             # 5. 완성된 챗봇 답변을 세션에 저장
#             st.session_state.messages.append({"role": "assistant", "content": response_content})
            
#         except Exception as e:
#             st.error(f"오류가 발생했습니다: {e}")



import streamlit as st
import pandas as pd
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="문서 요약 AI 비서", page_icon="📄", layout="wide")
st.title("📄 문서 요약 & 질의응답 챗봇")
st.caption("CSV 또는 MD 파일을 업로드하면 핵심 내용을 요약하고 추가 질문에 답변합니다.")

# ----------------- 사이드바 설정 -----------------
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password", help="sk-... 형태의 키를 입력하세요.")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"], index=0)
    
    st.divider()
    
    # 📌 요약 옵션 선택 (라디오 버튼)
    summary_option = st.radio(
        "📝 요약 옵션",
        ["짧게(3줄)", "보통(5-7줄)", "자세히(제한없이)"],
        index=1  # 기본값: 보통(5-7줄)
    )
    
    # 선택된 옵션에 따라 시스템 지침(System Prompt) 자동 매핑
    if summary_option == "짧게(3줄)":
        length_instruction = "문서의 가장 중요한 핵심만 추려서 정확히 3줄로 요약하세요. 군더더기 설명은 생략하세요."
    elif summary_option == "보통(5-7줄)":
        length_instruction = "문서의 핵심 맥락과 주요 포인트를 5줄에서 7줄 내외로 균형 있게 요약하세요."
    else:  # 자세히(제한없이)
        length_instruction = "분량 제한 없이 문서의 세부 내용, 수치, 시사점, 결론까지 구조화하여 상세하고 깊이 있게 정리하세요."

    # 최종 시스템 프롬프트 조립
    system_instruction = (
        f"당신은 데이터와 문서를 분석하는 전문 비서입니다.\n"
        f"제공된 문서 내용을 바탕으로 답변하며, 요약 시 다음 지침을 반드시 준수하세요:\n"
        f"- 요약 지침: {length_instruction}\n"
        f"- 질문에 답변할 때는 문서 내용을 최우선으로 근거 삼아 명확하게 설명하세요."
    )
    
    st.divider()
    
    # 세션 초기화 버튼
    if st.button("🗑️ 전체 대화 및 파일 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.file_context = ""
        st.session_state.file_summary_done = False
        st.rerun()

    st.markdown("[OpenAI API 키 발급받기](https://platform.openai.com/api-keys)")

# ----------------- 세션 상태 변수 초기화 -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_context" not in st.session_state:
    st.session_state.file_context = ""
if "file_summary_done" not in st.session_state:
    st.session_state.file_summary_done = False

# ----------------- 파일 업로더 -----------------
uploaded_file = st.file_uploader("요약할 문서를 업로드하세요 (CSV, MD 지원)", type=["csv", "md"])

# 새 파일이 업로드되었을 때 파일 내용 읽기
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.write("📋 **데이터 미리보기 (상위 5행)**")
            st.dataframe(df.head(5), use_container_width=True)
            # 프롬프트 전달용 텍스트 변환 (최대 50행)
            file_text = f"파일명: {uploaded_file.name}\n데이터 컬럼: {list(df.columns)}\n전체 행 수: {len(df)}\n상위 데이터 샘플:\n{df.head(50).to_string()}"
        
        elif uploaded_file.name.endswith(".md"):
            file_text = uploaded_file.read().decode("utf-8")
            with st.expander("📖 마크다운 원본 내용 보기"):
                st.markdown(file_text)

        # 새로운 파일이 올라오면 기존 대화 초기화
        if st.session_state.file_context != file_text:
            st.session_state.file_context = file_text
            st.session_state.messages = []
            st.session_state.file_summary_done = False

    except Exception as e:
        st.error(f"파일을 읽는 도중 오류가 발생했습니다: {e}")

# ----------------- 파일 자동 요약 실행 버튼 -----------------
if st.session_state.file_context and not st.session_state.file_summary_done:
    if st.button(f"✨ 문서 요약 시작하기 ({summary_option})", type="primary"):
        if not api_key:
            st.error("사이드바에서 OpenAI API Key를 먼저 입력해주세요.")
            st.stop()
            
        client = OpenAI(api_key=api_key)
        
        summary_prompt = f"다음 문서를 설정된 기준({summary_option})에 맞춰 요약해줘:\n\n{st.session_state.file_context}"
        st.session_state.messages.append({"role": "user", "content": f"업로드한 문서를 '{summary_option}' 옵션으로 요약해줘."})
        
        with st.chat_message("user"):
            st.markdown(f"업로드한 문서를 **{summary_option}** 옵션으로 요약해줘.")
            
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": summary_prompt}
                    ],
                    stream=True
                )
                summary_res = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": summary_res})
                st.session_state.file_summary_done = True
            except Exception as e:
                st.error(f"요약 중 오류가 발생했습니다: {e}")

# ----------------- 대화 기록 출력 -----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------- 추가 질의응답 (멀티턴) -----------------
if prompt := st.chat_input("문서에 대해 궁금한 점을 질문하세요..."):
    if not api_key:
        st.error("사이드바에서 OpenAI API Key를 먼저 입력해주세요.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 질의응답 시에도 파일 컨텍스트 및 선택된 요약 옵션 반영
    context_instruction = system_instruction
    if st.session_state.file_context:
        context_instruction += f"\n\n[참고할 원본 문서]:\n{st.session_state.file_context}"

    api_messages = [{"role": "system", "content": context_instruction}] + st.session_state.messages

    client = OpenAI(api_key=api_key)
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True
            )
            response_content = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response_content})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
