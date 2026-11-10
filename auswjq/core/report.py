"""상세 리포트(Markdown / HTML / JSON) 생성과 저장."""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

from .config import REPORT_DIR

SCORE_LABELS = {
    "overall": "종합", "content": "답변 내용", "logic": "논리성", "specificity": "구체성",
    "relevance": "직무 적합성", "delivery": "말하기", "speed": "말하기 속도",
    "fillers": "습관어", "voice": "목소리", "tone": "목소리 톤", "confidence": "자신감",
    "face": "표정·시선",
}


def averages(results: list[dict]) -> dict:
    keys = SCORE_LABELS.keys()
    avg = {}
    for k in keys:
        vals = [r["scores"][k] for r in results if r["scores"].get(k) is not None]
        avg[k] = round(sum(vals) / len(vals)) if vals else None
    return avg


def _fmt(v) -> str:
    return "-" if v is None else str(v)


def build_markdown(profile: dict, results: list[dict], summary: dict | None) -> str:
    avg = averages(results)
    lines = [
        "# AI 모의면접 리포트",
        "",
        f"- 일시: {datetime.now():%Y-%m-%d %H:%M}",
        f"- 회사 / 직무: {profile.get('company') or '-'} / {profile.get('role') or '-'} ({profile.get('level') or '-'})",
        f"- 답변 문항 수: {len(results)}",
        "",
        "## 종합 점수",
        "",
        "| 항목 | 점수 |",
        "|---|---|",
    ]
    lines += [f"| {SCORE_LABELS[k]} | {_fmt(v)} |" for k, v in avg.items()]
    if summary:
        lines += ["", "## AI 코치 총평", "", f"**{summary.get('headline', '')}**", "",
                  summary.get("overall_comment", ""), "", "### 강점"]
        lines += [f"- {s}" for s in summary.get("top_strengths", [])]
        lines += ["", "### 우선 개선할 점"]
        lines += [f"- {s}" for s in summary.get("priority_fixes", [])]
        lines += ["", "### 1주일 연습 계획"]
        lines += [f"{i}. {s}" for i, s in enumerate(summary.get("practice_plan", []), 1)]
        if summary.get("pass_probability"):
            lines += ["", f"> 합격 가능성: {summary['pass_probability']}"]

    for r in results:
        s = r["scores"]
        ev = r.get("content") or {}
        lines += [
            "", "---", "", f"## Q{r['index'] + 1}. {r['question']}", "",
            f"**종합 {_fmt(s['overall'])}점 ({r['grade']})** · 답변 {r['duration']}초 · "
            f"속도 {r['speech']['rate']} {r['speech']['unit']} ({r['speech']['label']})",
            "",
            f"- 논리성 {_fmt(s['logic'])} / 구체성 {_fmt(s['specificity'])} / 직무적합성 {_fmt(s['relevance'])}",
            f"- 말하기 {_fmt(s['delivery'])} / 목소리 톤 {_fmt(s['tone'])} / 자신감 {_fmt(s['confidence'])} / 표정·시선 {_fmt(s['face'])}",
            f"- 습관어: {r['fillers']['total']}회 ({r['fillers']['per_min']}/분) "
            + (", ".join(f"'{k}' {v}" for k, v in r['fillers']['counts'].items()) or "없음"),
            "", "**내 답변**", "", f"> {r['transcript'] or '(인식된 답변 없음)'}",
        ]
        if ev:
            lines += ["", f"**한 줄 평:** {ev.get('one_line', '')}", "", "**잘한 점**"]
            lines += [f"- {x}" for x in ev.get("strengths", [])]
            lines += ["", "**고칠 점**"]
            lines += [f"- {x}" for x in ev.get("improvements", [])]
            if ev.get("model_answer"):
                lines += ["", "**모범 답변 예시**", "", ev["model_answer"]]
            if ev.get("follow_up_questions"):
                lines += ["", "**예상 꼬리 질문**"]
                lines += [f"- {x}" for x in ev["follow_up_questions"]]
        lines += ["", "**목소리:** " + ", ".join(r["voice"].get("labels") or ["-"]),
                  "", "**표정:** " + ", ".join(r["face"].get("labels") or ["-"])]
    return "\n".join(lines)


def build_html(profile: dict, results: list[dict], summary: dict | None) -> str:
    """의존성 없이 보기 좋은 단일 HTML 리포트."""
    md = build_markdown(profile, results, summary)
    body = []
    in_list = False
    for line in md.splitlines():
        esc = html.escape(line)
        if line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        if in_list:
            body.append("</ul>")
            in_list = False
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("> "):
            body.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set(cells[0]) <= {"-"}:
                continue
            body.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in cells) + "</tr>")
        elif line == "---":
            body.append("<hr>")
        elif line.strip():
            text = esc.replace("**", "")
            body.append(f"<p>{text}</p>")
    if in_list:
        body.append("</ul>")
    content = _wrap_tables("\n".join(body))
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 모의면접 리포트</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
body{{font-family:Pretendard,system-ui,sans-serif;max-width:860px;margin:40px auto;padding:0 20px;color:#111827;background:#F7F8FC;line-height:1.7}}
h1{{font-size:30px;background:linear-gradient(90deg,#4F46E5,#06B6D4);-webkit-background-clip:text;color:transparent}}
h2{{margin-top:36px;font-size:21px}} h3{{font-size:17px;color:#4F46E5}}
table{{border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
td{{padding:8px 18px;border-bottom:1px solid #EEF0F5}} tr:first-child td{{font-weight:700;background:#EEF2FF}}
blockquote{{margin:0;padding:12px 16px;background:#fff;border-left:4px solid #4F46E5;border-radius:8px}}
hr{{border:none;border-top:1px solid #E5E7EB;margin:32px 0}}
</style></head><body>{content}</body></html>"""


def _wrap_tables(content: str) -> str:
    out, in_table = [], False
    for line in content.split("\n"):
        if line.startswith("<tr>"):
            if not in_table:
                out.append("<table>")
            in_table = True
            out.append(line)
        else:
            if in_table:
                out.append("</table>")
                in_table = False
            out.append(line)
    if in_table:
        out.append("</table>")
    return "\n".join(out)


def save_session(profile: dict, results: list[dict], summary: dict | None) -> Path:
    path = REPORT_DIR / f"interview_{datetime.now():%Y%m%d_%H%M%S}.json"
    slim = [{k: v for k, v in r.items() if k != "timeline"} for r in results]
    path.write_text(json.dumps({"profile": profile, "summary": summary, "results": slim},
                               ensure_ascii=False, indent=2), encoding="utf-8")
    return path
