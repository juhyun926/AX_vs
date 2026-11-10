"""음성 인식(Whisper), 습관어 체크, 말하기 속도 계산."""
from __future__ import annotations

import io
import re
from collections import Counter

from .config import OPENAI_STT_MODEL

# 확실한 습관어(간투사) — 1회당 1점
STRONG_FILLERS = {
    "음", "음음", "으음", "엄", "흠", "어", "어어", "아", "에", "으", "저기",
    "um", "umm", "uh", "uhm", "uhh", "er", "erm", "ah", "hmm", "a",
}
# 말버릇일 수도, 정상 단어일 수도 있는 표현 — 0.5점
WEAK_FILLERS = {
    "그", "저", "뭐", "막", "이제", "약간", "좀", "그니까", "그러니까", "일단",
    "뭔가", "사실", "like", "so", "basically", "actually",
}

# Whisper 는 기본적으로 '음/어' 를 지워버리므로, 프롬프트로 그대로 받아 적도록 유도합니다.
FILLER_PROMPT = (
    "음... 어, 그러니까 저는, 아 그, 음 이제 약간... um, uh. "
    "말한 그대로 습관어(음, 어, 아, 그, 저, 이제, 약간)까지 모두 받아 적습니다."
)


def transcribe(client, audio_bytes: bytes, mime: str = "audio/webm",
               language: str = "ko") -> dict:
    """OpenAI 음성 인식. {text, duration, segments} 반환."""
    ext = "webm"
    if "mp4" in mime or "m4a" in mime:
        ext = "mp4"
    elif "ogg" in mime:
        ext = "ogg"
    elif "wav" in mime:
        ext = "wav"
    file = io.BytesIO(audio_bytes)
    file.name = f"answer.{ext}"

    kwargs = dict(model=OPENAI_STT_MODEL, file=file, language=language[:2],
                  prompt=FILLER_PROMPT)
    if OPENAI_STT_MODEL == "whisper-1":
        kwargs["response_format"] = "verbose_json"
    resp = client.audio.transcriptions.create(**kwargs)

    text = getattr(resp, "text", "") or ""
    duration = getattr(resp, "duration", None)
    segments = []
    for seg in getattr(resp, "segments", None) or []:
        get = seg.get if isinstance(seg, dict) else lambda k, s=seg: getattr(s, k, None)
        segments.append({"start": get("start"), "end": get("end"), "text": get("text")})
    return {"text": text.strip(), "duration": duration, "segments": segments}


def detect_language(text: str) -> str:
    hangul = len(re.findall(r"[가-힣]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "ko" if hangul >= latin else "en"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[가-힣]+|[A-Za-z]+", text.lower())


def count_fillers(text: str, minutes: float) -> dict:
    lang = detect_language(text)
    tokens = tokenize(text)
    counts: Counter[str] = Counter()
    for tok in tokens:
        # 영어 답변에서는 관사 'a' 를 습관어로 세지 않습니다.
        if tok == "a" and lang == "en":
            continue
        if tok in STRONG_FILLERS or tok in WEAK_FILLERS:
            counts[tok] += 1
    strong = sum(v for k, v in counts.items() if k in STRONG_FILLERS)
    weak = sum(v for k, v in counts.items() if k in WEAK_FILLERS)
    weighted = strong + 0.5 * weak
    per_min = weighted / minutes if minutes > 0 else 0.0
    return {
        "counts": dict(counts.most_common()),
        "strong": strong,
        "weak": weak,
        "total": strong + weak,
        "per_min": round(per_min, 2),
    }


def speaking_rate(text: str, duration_sec: float) -> dict:
    """한국어는 음절/분(SPM), 영어는 단어/분(WPM)."""
    lang = detect_language(text)
    minutes = max(duration_sec, 1.0) / 60
    if lang == "ko":
        units = len(re.findall(r"[가-힣]", text))
        rate = units / minutes
        unit = "음절/분"
        if rate < 220:
            label = "많이 느림"
        elif rate < 260:
            label = "약간 느림"
        elif rate <= 350:
            label = "적정 속도"
        elif rate <= 400:
            label = "약간 빠름"
        else:
            label = "많이 빠름"
    else:
        units = len(re.findall(r"[A-Za-z']+", text))
        rate = units / minutes
        unit = "단어/분"
        if rate < 100:
            label = "많이 느림"
        elif rate < 120:
            label = "약간 느림"
        elif rate <= 165:
            label = "적정 속도"
        elif rate <= 190:
            label = "약간 빠름"
        else:
            label = "많이 빠름"
    return {"lang": lang, "units": units, "rate": round(rate), "unit": unit,
            "label": label}


def long_gaps(segments: list[dict], threshold: float = 1.5) -> int:
    """Whisper 구간 사이 1.5초 이상 공백 개수."""
    gaps = 0
    for prev, cur in zip(segments, segments[1:]):
        if prev.get("end") is not None and cur.get("start") is not None:
            if cur["start"] - prev["end"] >= threshold:
                gaps += 1
    return gaps
