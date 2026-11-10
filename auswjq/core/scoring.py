"""말하기·목소리·표정 지표를 0~100 점수로 바꾸는 규칙."""
from __future__ import annotations


def clamp(x: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, x))


def band_score(value: float, lo: float, hi: float, slope: float) -> float:
    """[lo, hi] 안이면 100점, 벗어나면 slope 만큼 감점."""
    if lo <= value <= hi:
        return 100.0
    dist = lo - value if value < lo else value - hi
    return clamp(100 - dist * slope)


# ---------------- 말하기 ----------------
def score_speed(rate: dict) -> float:
    if rate["units"] == 0:
        return 0.0
    if rate["lang"] == "ko":
        return round(band_score(rate["rate"], 270, 340, 0.5))
    return round(band_score(rate["rate"], 120, 160, 1.2))


def score_fillers(fillers: dict) -> float:
    # 분당 1회 이하면 만점, 이후 1회당 12점 감점
    return round(clamp(100 - max(0.0, fillers["per_min"] - 1) * 12))


# ---------------- 목소리 ----------------
def analyze_voice(v: dict, filler_per_min: float, eye_contact: float | None) -> dict:
    """브라우저(Web Audio)에서 측정한 값으로 톤·자신감 점수 계산."""
    if not v or v.get("frames", 0) == 0:
        return {"tone_score": None, "confidence_score": None, "labels": [],
                "details": {}}

    snr = (v.get("mean_db") or -60) - (v.get("noise_floor") or -60)
    volume_score = clamp((snr - 6) / 18 * 100)
    db_std = v.get("db_std") or 0
    stability_score = band_score(db_std, 2.5, 8, 9)

    st_std = v.get("pitch_semitone_std")
    if st_std is None:
        variation_score = 50.0
    else:
        variation_score = band_score(st_std, 1.6, 4.5, 30)

    voiced = v.get("voiced_ratio") or 0
    fluency_score = band_score(voiced, 0.45, 0.85, 150)
    pauses = v.get("long_pauses") or 0
    minutes = max((v.get("duration") or 1) / 60, 0.25)
    pause_score = clamp(100 - max(0, pauses / minutes - 2) * 15)
    first = v.get("first_voice_sec")
    start_score = 100.0 if first is None or first <= 3 else clamp(100 - (first - 3) * 12)
    filler_score = clamp(100 - max(0.0, filler_per_min - 1) * 12)
    eye_score = 70.0 if eye_contact is None else clamp(eye_contact * 110)

    tone = 0.6 * variation_score + 0.4 * stability_score
    confidence = (0.30 * volume_score + 0.15 * fluency_score + 0.10 * pause_score
                  + 0.10 * start_score + 0.15 * filler_score + 0.20 * eye_score)

    labels = []
    if snr < 12:
        labels.append("목소리가 작아요 — 조금 더 크게")
    elif snr > 18:
        labels.append("또렷한 성량")
    if st_std is not None:
        if st_std < 1.6:
            labels.append("톤이 단조로워요 — 강조할 단어에 억양을")
        elif st_std > 4.5:
            labels.append("톤 변화가 커서 떨리는 느낌")
        else:
            labels.append("자연스러운 억양")
    if db_std > 9:
        labels.append("성량이 들쭉날쭉해요")
    if pauses / minutes > 3:
        labels.append("긴 침묵이 잦아요")
    if first is not None and first > 4:
        labels.append(f"첫 마디까지 {first:.1f}초 — 바로 시작하는 연습을")

    return {
        "tone_score": round(tone),
        "confidence_score": round(confidence),
        "labels": labels,
        "details": {
            "성량(신호대잡음비)": f"{snr:.1f} dB",
            "성량 변화폭": f"{db_std:.1f} dB",
            "평균 음높이": f"{v['pitch_mean']:.0f} Hz" if v.get("pitch_mean") else "-",
            "억양 변화(반음)": f"{st_std:.2f}" if st_std is not None else "-",
            "발화 비율": f"{voiced * 100:.0f}%",
            "1.2초 이상 침묵": f"{pauses}회",
        },
    }


# ---------------- 표정 ----------------
def analyze_face(f: dict) -> dict:
    """MediaPipe Face Landmarker 블렌드셰이프 기반 표정·시선 점수."""
    if not f or f.get("face_frames", 0) == 0:
        return {"face_score": None, "labels": ["얼굴이 인식되지 않았어요"],
                "details": {}}

    presence = f.get("presence", 0)
    eye = f.get("eye_contact", 0)
    smile_ratio = f.get("smile_ratio", 0)
    tension = f.get("tension_ratio", 0)
    anxious = f.get("anxious_ratio", 0)
    blink = f.get("blink_per_min", 0)
    movement = f.get("head_movement", 0)

    eye_score = clamp(eye * 110)
    presence_score = clamp(presence * 100)
    smile_score = band_score(smile_ratio, 0.12, 0.55, 220)
    calm_score = clamp(100 - (tension + anxious) * 160)
    blink_score = band_score(blink, 8, 30, 3)
    stable_score = band_score(movement, 0, 2.5, 18)

    score = (0.40 * eye_score + 0.10 * presence_score + 0.20 * smile_score
             + 0.15 * calm_score + 0.075 * blink_score + 0.075 * stable_score)

    labels = []
    labels.append("시선 처리 좋음" if eye >= 0.7 else
                  "카메라(면접관)를 더 자주 바라보세요")
    if smile_ratio < 0.08:
        labels.append("표정이 굳어 있어요 — 가벼운 미소를")
    elif smile_ratio > 0.6:
        labels.append("미소가 과해 보일 수 있어요")
    else:
        labels.append("밝고 자연스러운 표정")
    if tension + anxious > 0.25:
        labels.append("미간·입꼬리에 긴장이 보여요")
    if blink > 35:
        labels.append("눈 깜빡임이 잦아요(긴장 신호)")
    if movement > 3.5:
        labels.append("고개 움직임이 많아요")

    return {
        "face_score": round(score),
        "labels": labels,
        "details": {
            "얼굴 인식률": f"{presence * 100:.0f}%",
            "시선 맞춤(아이컨택)": f"{eye * 100:.0f}%",
            "미소 비율": f"{smile_ratio * 100:.0f}%",
            "긴장/불안 표정": f"{(tension + anxious) * 100:.0f}%",
            "눈 깜빡임": f"{blink:.0f}회/분",
            "고개 흔들림": f"{movement:.2f}",
        },
    }


# ---------------- 종합 ----------------
def combine(content: float | None, delivery: float | None, voice: float | None,
            face: float | None) -> float | None:
    parts = [(content, 0.45), (delivery, 0.20), (voice, 0.15), (face, 0.20)]
    used = [(s, w) for s, w in parts if s is not None]
    if not used:
        return None
    total_w = sum(w for _, w in used)
    return round(sum(s * w for s, w in used) / total_w)


def grade(score: float | None) -> str:
    if score is None:
        return "-"
    for cut, g in [(90, "S"), (80, "A"), (70, "B"), (60, "C"), (50, "D")]:
        if score >= cut:
            return g
    return "F"
