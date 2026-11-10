"""맞춤형 면접 질문: 실제 기출 질문 웹 수집 + AI 예상 질문 생성."""
from __future__ import annotations

import json

from .config import OPENAI_SEARCH_MODEL, chat_json, extract_json

DEFAULT_QUESTIONS = [
    {"question": "1분 동안 자기소개를 해주세요.", "category": "인성",
     "intent": "핵심 역량과 지원 동기를 짧고 명확하게 전달하는지", "tip": "강점 1~2개 + 근거 경험 + 입사 후 포부"},
    {"question": "우리 회사에 지원한 이유는 무엇인가요?", "category": "인성",
     "intent": "회사에 대한 이해도와 진정성", "tip": "회사의 사업/가치와 내 경험을 연결"},
    {"question": "가장 어려웠던 문제를 해결한 경험을 말씀해 주세요.", "category": "경험",
     "intent": "문제 해결 과정과 주도성", "tip": "STAR 구조, 본인 역할과 수치화된 결과"},
    {"question": "팀원과 갈등이 있었을 때 어떻게 해결했나요?", "category": "협업",
     "intent": "커뮤니케이션과 갈등 관리 능력", "tip": "상대 입장 이해 → 합의 과정 → 결과와 배운 점"},
    {"question": "본인의 단점은 무엇이고 어떻게 보완하고 있나요?", "category": "인성",
     "intent": "자기 객관화와 성장 의지", "tip": "치명적이지 않은 단점 + 구체적 개선 행동"},
    {"question": "5년 후 본인의 모습은 어떨 것 같나요?", "category": "비전",
     "intent": "커리어 목표와 회사의 방향 일치 여부", "tip": "직무 전문성 + 회사 기여 관점"},
]

SEARCH_PROMPT = """웹 검색으로 '{company}' 의 '{role}' 직무(또는 유사 직무) 실제 면접 후기와 기출 질문을 찾아주세요.
잡플래닛, 블라인드, 링커리어, 캐치, 코멘토, 기업 채용 블로그, 뉴스 기사 등을 참고하세요.
찾은 내용을 바탕으로 아래 JSON 형식으로만 답하세요. 실제로 확인된 질문만 넣고, 지어내지 마세요.

{{
  "company_summary": "회사 인재상/최근 이슈/면접 전형 특징 요약 (3~4문장)",
  "interview_process": "알려진 면접 전형 (예: 1차 실무 → 2차 임원)",
  "questions": [
    {{"question": "실제 기출 질문", "category": "인성/직무/기술/경험/상황", "source": "출처 사이트명"}}
  ]
}}"""


def _citations(resp) -> list[dict]:
    sources, seen = [], set()
    for item in getattr(resp, "output", None) or []:
        for content in getattr(item, "content", None) or []:
            for ann in getattr(content, "annotations", None) or []:
                url = getattr(ann, "url", None)
                if url and url not in seen:
                    seen.add(url)
                    sources.append({"title": getattr(ann, "title", "") or url, "url": url})
    return sources


def collect_company_questions(client, company: str, role: str) -> dict:
    """OpenAI Responses API 의 web_search 도구로 실제 면접 질문을 수집합니다."""
    prompt = SEARCH_PROMPT.format(company=company, role=role or "전체")
    last_error = None
    for tool in ("web_search", "web_search_preview"):
        try:
            resp = client.responses.create(model=OPENAI_SEARCH_MODEL,
                                           tools=[{"type": tool}], input=prompt)
            data = extract_json(resp.output_text)
            data["sources"] = _citations(resp)
            data["mode"] = "web"
            data.setdefault("questions", [])
            return data
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    # 웹 검색을 쓸 수 없는 모델/계정이면 GPT 지식으로 대체
    data = chat_json(client, "면접 전문가로서 JSON 으로만 답하세요.",
                     prompt.replace("웹 검색으로", "알고 있는 정보로")
                     + "\n확실하지 않으면 source 를 'AI 추정' 으로 표기하세요.")
    data["sources"] = []
    data["mode"] = "fallback"
    data["error"] = str(last_error)[:200] if last_error else ""
    data.setdefault("questions", [])
    return data


GEN_SYSTEM = """당신은 해당 회사의 면접관입니다. 지원자 정보를 보고 실제 면접에서 나올 법한 예상 질문을 만듭니다.
JSON 으로만 답하세요:
{"questions": [
  {"question": "질문", "category": "인성/직무/기술/경험/상황/압박", "intent": "질문 의도", "tip": "답변 팁 한 줄"}
]}"""


def generate_questions(client, profile: dict, collected: list[dict], n: int,
                       categories: list[str]) -> list[dict]:
    user = f"""회사: {profile.get('company') or '미정'}
직무: {profile.get('role') or '미정'}
경력: {profile.get('level')}
원하는 질문 유형: {', '.join(categories) or '골고루'}
이력서/자기소개서/채용공고 (있으면 이를 근거로 꼬리질문형 질문 포함):
{(profile.get('resume') or '없음')[:3000]}

수집된 실제 기출 질문 (스타일 참고, 그대로 복사하지 말 것):
{json.dumps([q.get('question') for q in collected][:20], ensure_ascii=False)}

예상 질문 {n}개를 만들어 주세요. 쉬운 질문부터 어려운 질문 순으로 정렬하세요."""
    data = chat_json(client, GEN_SYSTEM, user, temperature=0.7)
    questions = [q for q in data.get("questions", []) if isinstance(q, dict) and q.get("question")]
    return questions[:n]
