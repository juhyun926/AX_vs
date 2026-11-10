"""AI 면접 코치 — Streamlit 메인 앱.

실행:  streamlit run app.py
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.interview_recorder import interview_recorder
from core import config
from core.analyzer import analyze_answer
from core.evaluator import live_tip, session_summary
from core.questions import DEFAULT_QUESTIONS, collect_company_questions, generate_questions
from core.report import SCORE_LABELS, averages, build_html, build_markdown, save_session
from core.speech import STRONG_FILLERS, WEAK_FILLERS

st.set_page_config(page_title="AI 면접 코치", page_icon="🎤", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)

def password_gate():
    """APP_PASSWORD 가 설정돼 있으면 비밀번호를 맞춰야 앱을 쓸 수 있습니다."""
    if not config.APP_PASSWORD or st.session_state.get("authed"):
        return
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div class="hero"><h1>🎤 AI 면접 코치</h1><p>비밀번호를 입력해 주세요.</p></div>',
                    unsafe_allow_html=True)
        with st.form("login"):
            pw = st.text_input("비밀번호", type="password")
            if st.form_submit_button("입장하기", type="primary", width="stretch"):
                if hmac.compare_digest(pw, config.APP_PASSWORD):
                    st.session_state.authed = True
                    st.rerun()
                st.error("비밀번호가 틀렸어요.")
    st.stop()


password_gate()

PAGES = ["① 맞춤 질문 만들기", "② 실전 면접 연습", "③ 종합 리포트"]
PERSIST_KEYS = ["company", "role", "level", "resume", "cats", "n_q", "max_sec",
                "live_on", "tip_interval", "lang"]

# ------------------------------------------------------------------ 상태
ss = st.session_state
for k in PERSIST_KEYS:  # 다른 페이지로 가도 입력값이 지워지지 않게
    if k in ss:
        ss[k] = ss[k]
DEFAULTS = {"company": "", "role": "", "level": "신입", "resume": "", "cats": ["인성", "직무", "경험"],
            "n_q": 7, "max_sec": 120, "live_on": True, "tip_interval": 15, "lang": "ko-KR"}
for k, v in DEFAULTS.items():
    ss.setdefault(k, v)
ss.setdefault("page", PAGES[0])
ss.setdefault("research", None)
ss.setdefault("generated", [])
ss.setdefault("questions", [])
ss.setdefault("q_idx", 0)
ss.setdefault("results", {})
ss.setdefault("processed", set())
ss.setdefault("seen_partials", set())
ss.setdefault("tips", {})
ss.setdefault("summary", None)


@st.cache_resource(show_spinner=False)
def get_client():
    return config.get_client()


client = get_client()


def profile() -> dict:
    return {"company": ss.get("company", ""), "role": ss.get("role", ""),
            "level": ss.get("level", "신입"), "resume": ss.get("resume", "")}


def goto(page: str):
    ss.page = page


# ------------------------------------------------------------------ UI 조각
def score_color(v):
    if v is None:
        return "#9ca3af"
    return "#10b981" if v >= 80 else "#4f46e5" if v >= 65 else "#f59e0b" if v >= 50 else "#ef4444"


def ring(score, grade_txt, label):
    pct = score or 0
    c = score_color(score)
    return f"""<div class="score-card"><div class="label">{label}</div>
      <div class="ring" style="background:conic-gradient({c} {pct * 3.6}deg,#eef0f6 0)">
      <div style="color:{c}">{'-' if score is None else score}<small>{grade_txt}</small></div></div></div>"""


def card(label, value, sub=""):
    c = score_color(value if isinstance(value, (int, float)) else None)
    shown = "-" if value is None else value
    return (f'<div class="score-card"><div class="label">{label}</div>'
            f'<div class="value" style="color:{c}">{shown}</div><div class="sub">{sub}</div></div>')


def pills(items, kind=""):
    return "".join(f'<span class="pill {kind}">{html.escape(str(i))}</span>' for i in items)


def highlight_fillers(text: str) -> str:
    fillers = STRONG_FILLERS | WEAK_FILLERS
    return re.sub(r"[가-힣]+|[A-Za-z]+",
                  lambda m: f"<mark>{m.group(0)}</mark>" if m.group(0).lower() in fillers else m.group(0),
                  html.escape(text))


def plot_layout(fig, height=280):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=10, r=10, t=30, b=10),
                      font=dict(family="Pretendard, sans-serif"), legend=dict(orientation="h", y=-0.2))
    return fig


def hero():
    idx = PAGES.index(ss.page)
    steps = "".join(f'<span class="step {"on" if i == idx else ""}">{p}</span>' for i, p in enumerate(PAGES))
    st.markdown(f"""<div class="hero"><h1>🎤 AI 면접 코치</h1>
      <p>카메라와 마이크로 실제처럼 연습하고, AI가 내용·말하기·목소리·표정까지 분석해 드려요.</p>
      <div class="steps">{steps}</div></div>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ 사이드바
with st.sidebar:
    st.markdown('<div class="side-logo">🎤 <span>AI Interview</span></div>'
                '<div class="side-sub">MediaPipe × GPT 실전 면접 코치</div>', unsafe_allow_html=True)
    st.radio("메뉴", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    if client:
        st.markdown(f'<span class="api-pill api-on">● OpenAI 연결됨</span>', unsafe_allow_html=True)
        st.caption(f"모델 `{config.OPENAI_MODEL}` · 음성 `{config.OPENAI_STT_MODEL}`")
    else:
        st.markdown('<span class="api-pill api-off">● API 키 없음</span>', unsafe_allow_html=True)
        st.caption(".env 에 OPENAI_API_KEY 를 넣으면 GPT 평가가 켜져요. 지금은 표정·목소리·속도 분석만 동작합니다.")
    st.divider()
    st.markdown("**연습 설정**")
    st.slider("답변 제한 시간(초)", min_value=30, max_value=300, step=10, key="max_sec")
    st.toggle("실시간 GPT 코칭", key="live_on", disabled=client is None)
    st.slider("코칭 주기(초)", min_value=8, max_value=40, key="tip_interval", disabled=client is None)
    st.selectbox("답변 언어", ["ko-KR", "en-US"], key="lang",
                 format_func=lambda x: "한국어" if x == "ko-KR" else "English")

hero()


# ================================================================== ① 질문 만들기
def page_questions():
    with st.container(border=True):
        st.subheader("🏢 지원 정보")
        c1, c2, c3 = st.columns([2, 2, 1.2])
        c1.text_input("지원 회사", key="company", placeholder="예: 네이버, 카카오, 삼성전자")
        c2.text_input("지원 직무", key="role", placeholder="예: 백엔드 개발자, 마케팅")
        c3.selectbox("경력", ["신입", "경력 1~3년", "경력 4~7년", "경력 8년+"], key="level")
        st.text_area("이력서 · 자기소개서 · 채용공고 (선택)", key="resume", height=130,
                     placeholder="붙여넣으면 내 경험을 파고드는 꼬리질문까지 만들어 드려요.")
        c4, c5 = st.columns([3, 1])
        c4.multiselect("질문 유형", ["인성", "직무", "기술", "경험", "상황", "압박"], key="cats")
        c5.number_input("예상 질문 수", min_value=3, max_value=15, key="n_q")

    no_key = client is None
    b1, b2, _ = st.columns([1.3, 1.3, 2])
    search = b1.button("🔍 실제 면접 질문 수집", width="stretch", disabled=no_key,
                       help="웹 검색으로 해당 회사의 실제 면접 후기·기출 질문을 모읍니다.")
    gen = b2.button("✨ AI 예상 질문 생성", type="primary", width="stretch", disabled=no_key)
    if no_key:
        st.info("API 키가 없어 기본 질문으로 연습할 수 있어요. 아래 목록에서 바로 시작하세요.")

    if search:
        if not ss.get("company"):
            st.warning("회사 이름을 입력해 주세요.")
        else:
            with st.spinner(f"'{ss.company}' 면접 후기를 웹에서 찾는 중… (20~40초)"):
                try:
                    ss.research = collect_company_questions(client, ss.company, ss.get("role", ""))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"수집 실패: {exc}")
    if gen:
        with st.spinner("지원 정보에 맞춘 예상 질문을 만드는 중…"):
            try:
                collected = (ss.research or {}).get("questions", [])
                ss.generated = generate_questions(client, profile(), collected,
                                                  int(ss.get("n_q", 7)), ss.get("cats", []))
            except Exception as exc:  # noqa: BLE001
                st.error(f"생성 실패: {exc}")

    # 수집 결과
    research = ss.research
    if research:
        with st.container(border=True):
            mode = "🌐 웹 검색 결과" if research.get("mode") == "web" else "🤖 AI 지식 기반 (웹 검색 불가)"
            st.subheader(f"📚 {ss.get('company', '')} 면접 정보 · {mode}")
            if research.get("company_summary"):
                st.write(research["company_summary"])
            if research.get("interview_process"):
                st.caption(f"면접 전형: {research['interview_process']}")
            if research.get("sources"):
                with st.expander(f"출처 {len(research['sources'])}개"):
                    for s in research["sources"]:
                        st.markdown(f"- [{s['title']}]({s['url']})")

    # 질문 목록 → 선택
    rows = []
    for q in (research or {}).get("questions", []):
        rows.append({"선택": True, "출처": f"기출 · {q.get('source', '-')}", "유형": q.get("category", ""),
                     "질문": q.get("question", ""), "_intent": "", "_tip": ""})
    for q in ss.generated:
        rows.append({"선택": True, "출처": "AI 예상", "유형": q.get("category", ""), "질문": q["question"],
                     "_intent": q.get("intent", ""), "_tip": q.get("tip", "")})
    if not rows:
        for q in DEFAULT_QUESTIONS:
            rows.append({"선택": True, "출처": "기본", "유형": q["category"], "질문": q["question"],
                         "_intent": q["intent"], "_tip": q["tip"]})

    st.subheader("📝 연습할 질문 고르기")
    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df, hide_index=True, width="stretch", key=f"editor_{len(rows)}_{hash(tuple(df['질문']))}",
        column_order=["선택", "출처", "유형", "질문"],
        column_config={"선택": st.column_config.CheckboxColumn(width="small"),
                       "질문": st.column_config.TextColumn(width="large")},
        disabled=["출처"], num_rows="dynamic",
    )
    chosen = edited[edited["선택"] == True]  # noqa: E712
    st.caption(f"{len(chosen)}개 선택됨 · 표의 마지막 행에 직접 질문을 추가할 수도 있어요.")
    def txt(x, default=""):
        return default if x is None or pd.isna(x) or not str(x).strip() else str(x)

    picked = [{"question": str(r["질문"]), "category": txt(r["유형"], "일반"), "intent": txt(r.get("_intent")),
               "tip": txt(r.get("_tip")), "source": txt(r["출처"], "직접 입력")}
              for _, r in chosen.iterrows() if isinstance(r["질문"], str) and r["질문"].strip()]
    st.button(f"🎬 선택한 {len(picked)}개 질문으로 면접 시작", type="primary", disabled=not picked,
              on_click=start_session, args=(picked,))


def start_session(picked: list[dict]):
    ss.questions = picked
    ss.q_idx, ss.results, ss.summary = 0, {}, None
    ss.page = PAGES[1]


# ================================================================== ② 실전 연습
def render_result(r: dict):
    s = r["scores"]
    ev = r.get("content")
    st.markdown("### 📊 이번 답변 분석")
    for e in r.get("errors", []):
        st.warning(e)
    st.markdown('<div class="score-grid">'
                + ring(s["overall"], r["grade"], "종합 점수")
                + card("답변 내용", s["content"], "논리·구체성·적합성")
                + card("말하기", s["delivery"], f"{r['speech']['rate']} {r['speech']['unit']}")
                + card("목소리·자신감", s["voice"], f"톤 {s['tone'] or '-'} · 자신감 {s['confidence'] or '-'}")
                + card("표정·시선", s["face"], "MediaPipe 분석")
                + "</div>", unsafe_allow_html=True)
    if ev and ev.get("one_line"):
        st.markdown(f'<div class="one-line">💬 {html.escape(ev["one_line"])}</div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["🧠 내용 평가", "🗣️ 말하기·습관어", "🎵 목소리·자신감", "😊 표정·시선", "✍️ 모범 답변"])

    with t1:
        if not ev:
            st.info("OpenAI API 키를 설정하면 GPT가 논리성·구체성·직무 적합성을 평가해요.")
        else:
            for key, name in [("logic", "논리성"), ("specificity", "구체성"), ("relevance", "질문 의도·직무 적합성")]:
                item = ev[key]
                st.markdown(f"**{name}** · {item['score']}점")
                st.progress(min(max(item["score"], 0), 100) / 100)
                st.caption(item.get("comment", ""))
            star = ev.get("star") or {}
            if star:
                st.markdown("**STAR 구조 점검**")
                st.dataframe(pd.DataFrame([{"단계": k.upper(), "평가": v} for k, v in star.items()]),
                             hide_index=True, width="stretch")
            c1, c2 = st.columns(2)
            c1.markdown("**👍 잘한 점**\n" + "\n".join(f"- {x}" for x in ev.get("strengths", [])))
            c2.markdown("**🔧 고칠 점**\n" + "\n".join(f"- {x}" for x in ev.get("improvements", [])))

    with t2:
        sp, fl = r["speech"], r["fillers"]
        c1, c2, c3 = st.columns(3)
        c1.metric("말하기 속도", f"{sp['rate']} {sp['unit']}", sp["label"], delta_color="off")
        c2.metric("습관어", f"{fl['total']}회", f"분당 {fl['per_min']}회", delta_color="off")
        c3.metric("답변 시간", f"{r['duration']:.0f}초")
        ideal = (270, 340, 450) if sp["lang"] == "ko" else (120, 160, 220)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=sp["rate"], number={"suffix": f" {sp['unit']}"},
            gauge={"axis": {"range": [0, ideal[2]]}, "bar": {"color": "#4f46e5"},
                   "steps": [{"range": [ideal[0], ideal[1]], "color": "#d1fae5"}]},
            title={"text": "적정 속도 구간(초록)"}))
        cg, cf = st.columns(2)
        cg.plotly_chart(plot_layout(gauge, 240), width="stretch", key=f"chart_{r['index']}_{r['timestamp']}_g")
        if fl["counts"]:
            bar = go.Figure(go.Bar(x=list(fl["counts"].keys()), y=list(fl["counts"].values()),
                                   marker_color=["#ef4444" if k in STRONG_FILLERS else "#f59e0b"
                                                 for k in fl["counts"]]))
            bar.update_layout(title="습관어 빈도 (빨강: 간투사, 주황: 말버릇)")
            cf.plotly_chart(plot_layout(bar, 240), width="stretch", key=f"chart_{r['index']}_{r['timestamp']}_f")
        else:
            cf.success("습관어가 거의 없어요! 👏")
        src = "Whisper 음성 인식" if r["transcript_source"] == "whisper" else "브라우저 실시간 자막"
        st.markdown(f"**내 답변** <span class='q-meta'>({src} · 노란색 = 습관어)</span>", unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-box">{highlight_fillers(r["transcript"]) or "(인식된 답변 없음)"}</div>',
                    unsafe_allow_html=True)

    timeline = pd.DataFrame(r.get("timeline") or [])

    with t3:
        v = r["voice"]
        c1, c2 = st.columns(2)
        c1.metric("목소리 톤", v["tone_score"] if v["tone_score"] is not None else "-")
        c2.metric("자신감", v["confidence_score"] if v["confidence_score"] is not None else "-")
        st.markdown(pills(v.get("labels") or ["-"]), unsafe_allow_html=True)
        if v.get("details"):
            st.dataframe(pd.DataFrame(v["details"].items(), columns=["지표", "값"]),
                         hide_index=True, width="stretch")
        if not timeline.empty:
            fig = go.Figure(go.Scatter(x=timeline["t"], y=timeline["vol"], fill="tozeroy",
                                       line=dict(color="#06b6d4"), name="성량"))
            fig.update_layout(title="시간별 성량 (dB, 주변 소음 대비)", xaxis_title="초")
            st.plotly_chart(plot_layout(fig), width="stretch", key=f"chart_{r['index']}_{r['timestamp']}_1")

    with t4:
        f = r["face"]
        raw = f.get("raw") or {}
        c1, c2 = st.columns([1, 1.3])
        with c1:
            st.metric("표정·시선 점수", f["face_score"] if f["face_score"] is not None else "-")
            st.markdown(pills(f.get("labels") or []), unsafe_allow_html=True)
            if f.get("details"):
                st.dataframe(pd.DataFrame(f["details"].items(), columns=["지표", "값"]),
                             hide_index=True, width="stretch")
        with c2:
            dist = raw.get("expression_dist") or {}
            if dist and sum(dist.values()) > 0:
                donut = go.Figure(go.Pie(labels=list(dist.keys()), values=list(dist.values()), hole=.6,
                                         marker_colors=["#10b981", "#94a3b8", "#ef4444", "#f59e0b"]))
                donut.update_layout(title="표정 분포")
                st.plotly_chart(plot_layout(donut, 260), width="stretch", key=f"chart_{r['index']}_{r['timestamp']}_2")
        if not timeline.empty and "eye" in timeline:
            fig = go.Figure()
            fig.add_scatter(x=timeline["t"], y=timeline["eye"] * 100, name="시선 맞춤 %", line=dict(color="#4f46e5"))
            fig.add_scatter(x=timeline["t"], y=timeline["smile"] * 100, name="미소 강도", line=dict(color="#10b981"))
            fig.update_layout(title="시간별 시선·표정", xaxis_title="초", yaxis_range=[0, 105])
            st.plotly_chart(plot_layout(fig), width="stretch", key=f"chart_{r['index']}_{r['timestamp']}_3")

    with t5:
        if ev and ev.get("model_answer"):
            st.markdown(ev["model_answer"])
            if ev.get("follow_up_questions"):
                st.markdown("**🔁 예상 꼬리 질문**")
                for i, fq in enumerate(ev["follow_up_questions"]):
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"- {fq}")
                    if c2.button("연습 추가", key=f"add_fq_{r['index']}_{i}"):
                        ss.questions.append({"question": fq, "category": "꼬리질문", "intent": "", "tip": ""})
                        st.toast("질문 목록 끝에 추가했어요!")
        else:
            st.info("API 키를 설정하면 모범 답변과 꼬리 질문을 만들어 드려요.")


def page_practice():
    questions = ss.questions or DEFAULT_QUESTIONS
    if not ss.questions:
        st.info("기본 질문으로 연습 중이에요. ①에서 회사·직무 맞춤 질문을 만들 수 있어요.")
    ss.q_idx = min(ss.q_idx, len(questions) - 1)
    idx = ss.q_idx
    q = questions[idx]

    c1, c2 = st.columns([3, 1])
    c1.markdown(f"**질문 {idx + 1} / {len(questions)}** <span class='q-meta'>· {q.get('category', '')}"
                f"{' · ' + q['source'] if q.get('source') else ''}</span>", unsafe_allow_html=True)
    c1.progress((len(ss.results)) / len(questions), text=f"답변 완료 {len(ss.results)}개")
    jump = c2.selectbox("질문 이동", range(len(questions)), index=idx, label_visibility="collapsed",
                        format_func=lambda i: f"Q{i + 1}. {questions[i]['question'][:22]}…"
                                              + (" ✅" if i in ss.results else ""))
    if jump != idx:
        ss.q_idx = jump
        st.rerun()
    if q.get("intent") or q.get("tip"):
        with st.expander("💡 질문 의도 & 답변 팁 (답변 전에 보면 연습 효과가 떨어질 수 있어요)"):
            st.write(f"**의도**: {q.get('intent') or '-'}")
            st.write(f"**팁**: {q.get('tip') or '-'}")

    rec_key = "rec_" + hashlib.md5(f"{idx}:{q['question']}".encode()).hexdigest()[:10]
    live_on = bool(ss.get("live_on", True)) and client is not None
    value = interview_recorder(
        q["question"], key=rec_key, live_tip=ss.tips.get(rec_key, ""), live_coaching=live_on,
        tip_interval=int(ss.get("tip_interval", 15)), max_seconds=int(ss.get("max_sec", 120)),
        lang=ss.get("lang", "ko-KR"),
    )

    if isinstance(value, dict):
        # 답변 중간: 실시간 GPT 코칭
        if value.get("type") == "partial" and live_on:
            pid = f"{rec_key}:{value.get('seq')}"
            if pid not in ss.seen_partials:
                ss.seen_partials.add(pid)
                try:
                    ss.tips[rec_key] = live_tip(client, q["question"], value.get("transcript", ""),
                                                value.get("stats", {}))
                except Exception as exc:  # noqa: BLE001
                    ss.tips[rec_key] = f"⚠️ 코칭 오류: {str(exc)[:40]}"
                st.rerun()
        # 답변 완료: 전체 분석
        elif value.get("type") == "final" and value.get("id") not in ss.processed:
            ss.processed.add(value["id"])
            ss.tips.pop(rec_key, None)
            with st.status("AI가 답변을 분석하고 있어요…", expanded=True) as status:
                st.write("🎧 음성 인식 · 습관어 · 말하기 속도 분석")
                st.write("😊 표정 · 시선 · 목소리 톤 점수 계산")
                if client:
                    st.write("🧠 GPT 논리성 · 구체성 평가")
                ss.results[idx] = analyze_answer(client, value, profile(), q, idx, ss.get("lang", "ko-KR"))
                ss.summary = None
                status.update(label="분석 완료!", state="complete", expanded=False)

    if idx in ss.results:
        render_result(ss.results[idx])

    st.divider()
    n1, n2, n3 = st.columns(3)
    if n1.button("← 이전 질문", disabled=idx == 0, width="stretch"):
        ss.q_idx -= 1
        st.rerun()
    if n2.button("다음 질문 →", type="primary", disabled=idx >= len(questions) - 1, width="stretch"):
        ss.q_idx += 1
        st.rerun()
    n3.button("📑 종합 리포트 보기", width="stretch", disabled=not ss.results,
              on_click=goto, args=(PAGES[2],))


# ================================================================== ③ 리포트
def page_report():
    results = [ss.results[k] for k in sorted(ss.results)]
    if not results:
        st.info("아직 답변한 질문이 없어요. ② 실전 면접 연습에서 답변해 보세요.")
        st.button("🎬 연습하러 가기", type="primary", on_click=goto, args=(PAGES[1],))
        return

    avg = averages(results)
    from core.scoring import grade

    st.markdown('<div class="score-grid">'
                + ring(avg["overall"], grade(avg["overall"]), "평균 종합")
                + card("논리성", avg["logic"]) + card("구체성", avg["specificity"])
                + card("직무 적합성", avg["relevance"]) + card("말하기", avg["delivery"])
                + card("목소리 톤", avg["tone"]) + card("자신감", avg["confidence"])
                + card("표정·시선", avg["face"]) + "</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        axes = ["logic", "specificity", "relevance", "delivery", "tone", "confidence", "face"]
        axes = [a for a in axes if avg.get(a) is not None]
        if len(axes) >= 3:
            vals = [avg[a] for a in axes]
            radar = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=[SCORE_LABELS[a] for a in axes + axes[:1]],
                                              fill="toself", line=dict(color="#4f46e5"),
                                              fillcolor="rgba(79,70,229,.2)"))
            radar.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), title="역량 레이더")
            st.plotly_chart(plot_layout(radar, 360), width="stretch")
    with c2:
        bar = go.Figure(go.Bar(x=[f"Q{r['index'] + 1}" for r in results],
                               y=[r["scores"]["overall"] or 0 for r in results],
                               marker_color=[score_color(r["scores"]["overall"]) for r in results],
                               text=[r["grade"] for r in results], textposition="outside"))
        bar.update_layout(title="문항별 종합 점수", yaxis_range=[0, 110])
        st.plotly_chart(plot_layout(bar, 360), width="stretch")

    table = pd.DataFrame([{
        "문항": f"Q{r['index'] + 1}", "질문": r["question"], "종합": r["scores"]["overall"], "등급": r["grade"],
        "내용": r["scores"]["content"], "말하기": r["scores"]["delivery"], "목소리": r["scores"]["voice"],
        "표정": r["scores"]["face"], "속도": f"{r['speech']['rate']} {r['speech']['unit']}",
        "습관어": r["fillers"]["total"],
    } for r in results])
    st.dataframe(table, hide_index=True, width="stretch")

    # GPT 총평
    st.subheader("🧑‍🏫 AI 코치 총평")
    if client:
        if ss.summary is None and st.button("✨ 총평 생성하기", type="primary"):
            with st.spinner("전체 답변을 종합하는 중…"):
                try:
                    ss.summary = session_summary(client, profile(), results)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"총평 생성 실패: {exc}")
        sm = ss.summary
        if sm:
            st.markdown(f'<div class="one-line">🏁 {html.escape(sm.get("headline", ""))}</div>',
                        unsafe_allow_html=True)
            st.write(sm.get("overall_comment", ""))
            a, b, c = st.columns(3)
            a.markdown("**💪 강점**\n" + "\n".join(f"- {x}" for x in sm.get("top_strengths", [])))
            b.markdown("**🎯 우선 개선**\n" + "\n".join(f"- {x}" for x in sm.get("priority_fixes", [])))
            c.markdown("**🗓️ 1주일 연습 계획**\n" + "\n".join(f"{i}. {x}" for i, x in
                                                          enumerate(sm.get("practice_plan", []), 1)))
            if sm.get("pass_probability"):
                st.caption(f"합격 가능성 예측: {sm['pass_probability']}")
    else:
        st.info("API 키를 설정하면 GPT가 전체 세션 총평과 연습 계획을 만들어 드려요.")

    with st.expander("📄 문항별 상세 보기"):
        for r in results:
            st.markdown(f"#### Q{r['index'] + 1}. {r['question']}")
            render_result(r)

    # 다운로드
    st.subheader("⬇️ 리포트 저장")
    md = build_markdown(profile(), results, ss.summary)
    d1, d2, d3, d4 = st.columns(4)
    d1.download_button("Markdown", md, "interview_report.md", "text/markdown", width="stretch")
    d2.download_button("HTML", build_html(profile(), results, ss.summary), "interview_report.html",
                       "text/html", width="stretch")
    d3.download_button("JSON", json.dumps({"profile": profile(), "summary": ss.summary, "results": results},
                                          ensure_ascii=False, indent=2),
                       "interview_report.json", "application/json", width="stretch")
    if d4.button("💾 data/reports 에 저장", width="stretch"):
        path = save_session(profile(), results, ss.summary)
        st.success(f"저장됨: {path.name}")


# ------------------------------------------------------------------ 라우팅
if ss.page == PAGES[0]:
    page_questions()
elif ss.page == PAGES[1]:
    page_practice()
else:
    page_report()
