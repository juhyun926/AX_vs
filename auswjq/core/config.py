"""환경 변수(.env) 로드와 OpenAI 클라이언트 / 공통 호출 함수."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _load_env() -> None:
    """프로젝트 폴더의 .env 를 우선 읽고, 비어 있는 값은 상위 폴더 .env 에서 채웁니다."""
    for path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
        for key, value in dotenv_values(path).items():
            if value and not value.startswith("sk-your") and not os.getenv(key):
                os.environ[key] = value


ENV_KEYS = ["OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_SEARCH_MODEL", "OPENAI_STT_MODEL", "APP_PASSWORD"]


def _load_streamlit_secrets() -> None:
    """배포 환경(Streamlit Cloud)에서는 .env 대신 Secrets 설정값을 씁니다."""
    try:
        import streamlit as st

        for key in ENV_KEYS:
            if not os.getenv(key) and key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:  # noqa: BLE001  secrets.toml 이 없으면 그냥 넘어감
        pass


_load_env()
_load_streamlit_secrets()

APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_SEARCH_MODEL = os.getenv("OPENAI_SEARCH_MODEL", OPENAI_MODEL).strip()
OPENAI_STT_MODEL = os.getenv("OPENAI_STT_MODEL", "whisper-1").strip()


def has_api_key() -> bool:
    return bool(OPENAI_API_KEY) and not OPENAI_API_KEY.startswith("sk-your")


def get_client():
    """API 키가 있으면 OpenAI 클라이언트를, 없으면 None 을 돌려줍니다."""
    if not has_api_key():
        return None
    from openai import OpenAI

    return OpenAI(api_key=OPENAI_API_KEY)


def extract_json(text: str) -> dict:
    """모델 응답 문자열에서 JSON 객체를 꺼냅니다(코드블록 등이 섞여 있어도 처리)."""
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return {}


def chat_json(client, system: str, user: str, model: str | None = None,
              temperature: float = 0.4) -> dict:
    """JSON 형식으로 답하는 Chat Completions 호출.

    gpt-5 / o 시리즈처럼 temperature 를 지원하지 않는 모델이면 자동으로 빼고 다시 호출합니다.
    """
    model = model or OPENAI_MODEL
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    kwargs = dict(model=model, messages=messages,
                  response_format={"type": "json_object"})
    try:
        resp = client.chat.completions.create(temperature=temperature, **kwargs)
    except Exception as exc:  # noqa: BLE001
        if "temperature" not in str(exc):
            raise
        resp = client.chat.completions.create(**kwargs)
    return extract_json(resp.choices[0].message.content or "")


def chat_text(client, system: str, user: str, model: str | None = None,
              temperature: float = 0.5) -> str:
    model = model or OPENAI_MODEL
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    try:
        resp = client.chat.completions.create(model=model, messages=messages,
                                              temperature=temperature)
    except Exception as exc:  # noqa: BLE001
        if "temperature" not in str(exc):
            raise
        resp = client.chat.completions.create(model=model, messages=messages)
    return (resp.choices[0].message.content or "").strip()
