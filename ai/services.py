"""Thin Ollama HTTP client used by the AI caption-suggestion endpoint.

Swapping providers later is a one-file change: keep the public function
`suggest_captions` and route the HTTP call elsewhere.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests

from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
REQUEST_TIMEOUT_SECONDS = 30


def _fallback(caption: str) -> dict[str, Any]:
    """Return a safe result when Ollama is unreachable or returns junk."""
    text = (caption or "").strip()
    return {
        "captions": [
            text or "Making memories on campus.",
            f"{text[:60]} ✨".strip(),
            f"Just another day at CampusFind — {text[:40]}".strip(),
        ],
        "hashtags": ["campuslife", "campusfind", "college"],
        "emojis": ["📸", "✨", "🎓"],
        "source": "fallback",
    }


def _normalize(raw: Any) -> dict[str, Any] | None:
    """Pull the expected keys out of the model's JSON-ish response."""
    if not isinstance(raw, dict):
        return None
    captions = raw.get("captions") or []
    hashtags = raw.get("hashtags") or []
    emojis = raw.get("emojis") or []

    captions = [str(c).strip() for c in captions if str(c).strip()][:3]
    hashtags = [
        str(h).strip().lstrip("#").lower()
        for h in hashtags
        if str(h).strip()
    ][:8]
    emojis = [str(e).strip() for e in emojis if str(e).strip()][:5]

    if not captions:
        return None
    return {
        "captions": captions,
        "hashtags": hashtags,
        "emojis": emojis,
        "source": "ollama",
    }


def suggest_captions(caption: str) -> dict[str, Any]:
    """Ask the local Ollama model for caption rewrites + hashtags + emojis.

    Always returns a dict with keys: captions (list[str]), hashtags (list[str]),
    emojis (list[str]). Falls back to a static result on any error so the UI
    never breaks if Ollama is down.
    """
    user_prompt = build_user_prompt(caption)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Ollama request failed: %s", exc)
        return _fallback(caption)

    try:
        payload = response.json().get("response", "")
        parsed = json.loads(payload) if isinstance(payload, str) else payload
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        logger.warning("Ollama returned non-JSON: %s", exc)
        return _fallback(caption)

    normalized = _normalize(parsed)
    if normalized is None:
        return _fallback(caption)
    return normalized
