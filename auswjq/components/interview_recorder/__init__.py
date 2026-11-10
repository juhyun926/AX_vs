"""카메라·마이크 실시간 면접 녹화 컴포넌트 (브라우저에서 MediaPipe 얼굴 분석).

프론트엔드는 frontend/ 폴더의 순수 HTML/JS 로 되어 있어 npm 빌드가 필요 없습니다.
"""
from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_FRONTEND = Path(__file__).parent / "frontend"
_component = components.declare_component("interview_recorder", path=str(_FRONTEND))


def interview_recorder(question: str, *, key: str, live_tip: str = "",
                       live_coaching: bool = True, tip_interval: int = 15,
                       max_seconds: int = 120, lang: str = "ko-KR",
                       height: int = 720):
    """질문을 보여주고 답변을 녹화합니다.

    반환값
      - None: 아직 아무 일도 없음
      - {"type": "partial", ...}: 답변 중간 자막(실시간 GPT 코칭용)
      - {"type": "final", ...}: 녹음 오디오(base64) + 표정/목소리 지표
    """
    return _component(question=question, live_tip=live_tip,
                      live_coaching=live_coaching, tip_interval=tip_interval,
                      max_seconds=max_seconds, lang=lang, height=height,
                      key=key, default=None)
