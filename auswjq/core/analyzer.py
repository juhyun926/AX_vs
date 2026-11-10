"""녹화 컴포넌트가 보낸 데이터 → 한 문항의 분석 결과(dict)."""
from __future__ import annotations

import base64
from datetime import datetime

from . import scoring, speech
from .evaluator import content_score, evaluate_answer


def analyze_answer(client, payload: dict, profile: dict, question: dict,
                   index: int, lang: str = "ko-KR") -> dict:
    duration = float(payload.get("duration") or 0)
    errors: list[str] = []

    # 1) 음성 → 텍스트 (Whisper 우선, 실패하면 브라우저 실시간 자막 사용)
    transcript, source, segments = "", "browser", []
    if client and payload.get("audio_b64"):
        try:
            audio = base64.b64decode(payload["audio_b64"])
            stt = speech.transcribe(client, audio, payload.get("mime", "audio/webm"), lang)
            transcript, segments, source = stt["text"], stt["segments"], "whisper"
        except Exception as exc:  # noqa: BLE001
            errors.append(f"음성 인식 실패 → 브라우저 자막 사용 ({str(exc)[:120]})")
    if not transcript:
        transcript = (payload.get("transcript_live") or "").strip()
        source = "browser"

    # 실제 말한 시간: 첫 발화 ~ 녹음 종료
    first_voice = (payload.get("voice") or {}).get("first_voice_sec") or 0
    speak_sec = max(duration - first_voice, 1.0)
    minutes = speak_sec / 60

    # 2) 말하기 속도 · 습관어
    rate = speech.speaking_rate(transcript, speak_sec)
    fillers = speech.count_fillers(transcript, minutes)
    speed_score = scoring.score_speed(rate)
    filler_score = scoring.score_fillers(fillers)
    rate["score"] = speed_score
    fillers["score"] = filler_score
    delivery_score = round((speed_score + filler_score) / 2) if transcript else None

    # 3) 표정 · 목소리
    face = scoring.analyze_face(payload.get("face") or {})
    face["raw"] = payload.get("face") or {}
    eye = face["raw"].get("eye_contact") if face["face_score"] is not None else None
    voice = scoring.analyze_voice(payload.get("voice") or {}, fillers["per_min"], eye)
    voice["raw"] = payload.get("voice") or {}
    if segments:
        voice["details"]["긴 공백(음성인식 기준)"] = f"{speech.long_gaps(segments)}회"

    voice_score = None
    if voice["tone_score"] is not None:
        voice_score = round((voice["tone_score"] + voice["confidence_score"]) / 2)

    # 4) GPT 내용 평가 (논리성 · 구체성 · 직무 적합성)
    evaluation = None
    if client:
        try:
            evaluation = evaluate_answer(client, profile, question, transcript, {
                "답변시간(초)": round(duration),
                "말하기속도": f"{rate['rate']} {rate['unit']} ({rate['label']})",
                "습관어": fillers["counts"],
                "목소리": voice["labels"],
                "표정": face["labels"],
            })
        except Exception as exc:  # noqa: BLE001
            errors.append(f"GPT 평가 실패: {str(exc)[:160]}")

    c_score = content_score(evaluation)
    overall = scoring.combine(c_score, delivery_score, voice_score, face["face_score"])

    return {
        "index": index,
        "question": question.get("question"),
        "category": question.get("category", "일반"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "duration": round(duration, 1),
        "transcript": transcript,
        "transcript_source": source,
        "speech": rate,
        "fillers": fillers,
        "voice": voice,
        "face": face,
        "content": evaluation,
        "timeline": payload.get("timeline") or [],
        "scores": {
            "content": c_score,
            "logic": evaluation["logic"]["score"] if evaluation else None,
            "specificity": evaluation["specificity"]["score"] if evaluation else None,
            "relevance": evaluation["relevance"]["score"] if evaluation else None,
            "speed": speed_score,
            "fillers": filler_score,
            "delivery": delivery_score,
            "tone": voice["tone_score"],
            "confidence": voice["confidence_score"],
            "voice": voice_score,
            "face": face["face_score"],
            "overall": overall,
        },
        "grade": scoring.grade(overall),
        "errors": errors,
    }
