"""NVIDIA Nemotron and OpenAI-compatible LLM client with caching and offline safety."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
)


def strip_markdown_json_fences(content: str) -> str:
    """Clean markdown code fences (e.g. ```json ... ```) from LLM output."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        # Remove first line if it starts with ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line if it starts with ```
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    return content


class LLMClient:
    """Safe, schema-constrained LLM client supporting cache, mock, and openai_compatible providers."""

    def __init__(
        self,
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.provider = (provider or os.getenv("LLM_PROVIDER", LLM_PROVIDER)).lower()
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", LLM_BASE_URL)).rstrip("/")
        self.model = model or os.getenv("LLM_MODEL", LLM_MODEL)
        self.api_key = api_key or os.getenv("LLM_API_KEY", LLM_API_KEY)
        self.timeout = timeout if timeout is not None else int(os.getenv("LLM_TIMEOUT_SECONDS", LLM_TIMEOUT_SECONDS))
        self.temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", LLM_TEMPERATURE))
        self.max_tokens = max_tokens if max_tokens is not None else int(os.getenv("LLM_MAX_TOKENS", LLM_MAX_TOKENS))

    def _call_live_api(
        self, messages: List[Dict[str, str]], use_json_format: bool = True
    ) -> Optional[str]:
        """Make HTTP POST request to OpenAI-compatible chat completions endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "ScrollSense/1.0",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if use_json_format:
            payload["response_format"] = {"type": "json_object"}

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                resp_json = json.loads(resp_bytes.decode("utf-8"))
                choices = resp_json.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "")
                return None
        except urllib.error.HTTPError as err:
            # If response_format json_object is rejected (e.g. 400 Bad Request), retry once without it
            if use_json_format and err.code in (400, 422):
                return self._call_live_api(messages, use_json_format=False)
            return None
        except Exception:
            return None

    def complete_chat(
        self,
        messages: List[Dict[str, str]],
        mock_response: Optional[str] = None,
        retries: int = 2,
    ) -> Optional[str]:
        """Complete a chat prompt with automatic retries and fail-safe handling."""
        if self.provider == "mock":
            return mock_response or '{"status": "mocked"}'

        if self.provider in ("cache", "offline"):
            return mock_response or None

        if self.provider == "openai_compatible":
            if not self.api_key:
                return mock_response or None

            for attempt in range(retries + 1):
                try:
                    res = self._call_live_api(messages, use_json_format=True)
                    if res is not None:
                        return res
                except Exception:
                    pass
            return mock_response or None

        return mock_response or None

    def complete_json(
        self,
        messages: List[Dict[str, str]],
        mock_json: Optional[Dict[str, Any]] = None,
        mock_response: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, Any]], bool]:
        """Call LLM and parse JSON output. Returns (parsed_dict, is_fallback)."""
        mock_str = mock_response if mock_response is not None else (json.dumps(mock_json) if mock_json is not None else None)
        raw_text = self.complete_chat(messages, mock_response=mock_str)
        if not raw_text:
            return mock_json, True

        cleaned_text = strip_markdown_json_fences(raw_text)
        try:
            parsed = json.loads(cleaned_text)
            if isinstance(parsed, dict):
                return parsed, False
            return mock_json, True
        except Exception:
            return mock_json, True
