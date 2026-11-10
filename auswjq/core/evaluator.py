"""GPT 기반 답변 평가 · 실시간 코칭 · 세션 총평."""
from __future__ import annotations

import json

from .config import chat_json, chat_text

EVAL_SYSTEM = """당신은 대기업·스타트업 채용 경험이 15년 이상인 시니어 면접관이자 면접 코치입니다.
지원자의 답변(음성 인식 텍스트)을 냉정하지만 따뜻하게 평가합니다.
음성 인식 특성상 오타나 띄어쓰기 오류는 감점하지 마세요.
반드시 아래 JSON 형식으로만 답하세요.

{
  "logic": {"score": 0-100, "comment": "논리성: 두괄식인지, 주장-근거-결론 흐름이 자연스러운지"},
  "specificity": {"score": 0-100, "comment": "구체성: 수치·사례·본인 역할·결과가 드러나는지"},
  "relevance": {"score": 0-100, "comment": "질문 의도·직무 적합성: 질문에 정확히 답했고 직무와 연결되는지"},
  "star": {"situation": "있음/부족/없음 + 한줄", "task": "...", "action": "...", "result": "..."},
  "strengths": ["잘한 점 2~3개"],
  "improvements": ["구체적으로 고칠 점 2~3개 (어떻게 바꾸면 되는지까지)"],
  "model_answer": "지원자의 경험을 살려 다듬은 모범 답변 (300~500자)",
  "follow_up_questions": ["이 답변을 들은 면접관이 할 꼬리 질문 2~3개"],
  "one_line": "한 줄 총평"
}"""


def evaluate_answer(client, profile: dict, question: dict, transcript: str,
                    delivery: dict) -> dict:
    if not transcript.strip():
        return {
            "logic": {"score": 0, "comment": "인식된 답변이 없습니다."},
            "specificity": {"score": 0, "comment": "-"},
            "relevance": {"score": 0, "comment": "-"},
            "star": {}, "strengths": [], "improvements": ["마이크 상태를 확인하고 다시 답변해 보세요."],
            "model_answer": "", "follow_up_questions": [], "one_line": "답변이 인식되지 않았어요.",
        }
    user = f"""[지원 정보]
회사: {profile.get('company') or '미입력'}
직무: {profile.get('role') or '미입력'}
경력: {profile.get('level') or '미입력'}
참고(이력/공고): {(profile.get('resume') or '')[:1500]}

[질문] ({question.get('category', '일반')})
{question.get('question')}
질문 의도: {question.get('intent', '-')}

[지원자 답변 — 음성 인식]
{transcript}

[전달력 측정값]
{json.dumps(delivery, ensure_ascii=False)}
"""
    data = chat_json(client, EVAL_SYSTEM, user, temperature=0.3)
    for key in ("logic", "specificity", "relevance"):
        item = data.get(key) or {}
        try:
            item["score"] = int(float(item.get("score", 0)))
        except (TypeError, ValueError):
            item["score"] = 0
        item.setdefault("comment", "")
        data[key] = item
    for key in ("strengths", "improvements", "follow_up_questions"):
        if not isinstance(data.get(key), list):
            data[key] = [str(data[key])] if data.get(key) else []
    data.setdefault("model_answer", "")
    data.setdefault("one_line", "")
    data.setdefault("star", {})
    return data


def content_score(evaluation: dict | None) -> float | None:
    if not evaluation:
        return None
    scores = [evaluation[k]["score"] for k in ("logic", "specificity", "relevance")
              if isinstance(evaluation.get(k), dict)]
    return round(sum(scores) / len(scores)) if scores else None


LIVE_SYSTEM = """당신은 면접 실전 코치입니다. 지원자가 지금 답변하는 중입니다.
지금까지의 답변 일부와 측정값을 보고, 지금 당장 적용할 수 있는 코칭 한마디를 주세요.
- 한국어 35자 이내, 한 문장, 이모지 1개로 시작
- 칭찬 또는 방향 제시 (예: "📊 성과를 숫자로 말해보세요", "👍 두괄식 좋아요, 근거 하나 더!")
- 다른 말은 하지 마세요."""


def live_tip(client, question: str, partial: str, stats: dict) -> str:
    user = (f"질문: {question}\n지금까지 답변: {partial[-1200:]}\n"
            f"측정값: {json.dumps(stats, ensure_ascii=False)}")
    tip = chat_text(client, LIVE_SYSTEM, user, temperature=0.6)
    return tip.strip().strip('"')[:60]


SUMMARY_SYSTEM = """당신은 면접 코치입니다. 모의면접 세션 전체 결과를 보고 종합 리포트를 작성합니다.
JSON 으로만 답하세요:
{
  "headline": "한 줄 총평",
  "overall_comment": "전체 평가 (4~6문장)",
  "top_strengths": ["강점 3개"],
  "priority_fixes": ["가장 먼저 고칠 점 3개 (구체적 연습 방법 포함)"],
  "practice_plan": ["다음 1주일 연습 계획 3~5단계"],
  "pass_probability": "현재 상태로 본 합격 가능성 (낮음/보통/높음 + 이유 한 줄)"
}"""


def session_summary(client, profile: dict, results: list[dict]) -> dict:
    compact = []
    for r in results:
        ev = r.get("content") or {}
        compact.append({
            "question": r["question"],
            "scores": r["scores"],
            "one_line": ev.get("one_line"),
            "improvements": ev.get("improvements"),
            "speed": r["speech"]["label"],
            "fillers_per_min": r["fillers"]["per_min"],
            "voice": r["voice"].get("labels"),
            "face": r["face"].get("labels"),
        })
    user = (f"지원: {profile.get('company')} / {profile.get('role')} / {profile.get('level')}\n"
            f"결과: {json.dumps(compact, ensure_ascii=False)}")
    return chat_json(client, SUMMARY_SYSTEM, user, temperature=0.4)
