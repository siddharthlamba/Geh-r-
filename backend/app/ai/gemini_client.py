"""
Local Offline LLM Client for Gehor using Ollama (Qwen 3 4B).
100% Privacy-First, Local Offline Execution. No external Cloud API keys required.
"""
import os
import json
import logging
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
import ollama

from ..config import OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS

logger = logging.getLogger("gehor.ai.local_ollama")

DEFAULT_MODEL = "qwen3:4b"

class GeminiInferenceResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    provider: str  # "ollama_offline" or "rule_fallback"
    model: str
    latency_ms: float
    error_message: Optional[str] = None
    is_quota_exhausted: bool = False

# Type alias
OllamaInferenceResult = GeminiInferenceResult

class GeminiClient:
    """
    Offline AI Client powered 100% locally by Ollama.
    Runs Qwen 3 4B locally on the host machine without cloud dependencies or API keys.
    """
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL") or OLLAMA_MODEL or DEFAULT_MODEL
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", str(OLLAMA_TIMEOUT_SECONDS)))
        logger.info(f"Ollama Local Client initialized for offline inference with model '{self.model}'.")

    @property
    def is_available(self) -> bool:
        # System is entirely self-hosted offline. No external cloud API keys required.
        return True

    def generate_structured_json(
        self,
        prompt: str,
        system_instruction: str = "You are an institutional complaint management intelligence engine. Return valid JSON only.",
        temperature: float = 0.1
    ) -> GeminiInferenceResult:
        """
        Executes a prompt against local Ollama model with strict JSON formatting.
        Uses ollama.chat() with format='json' and temperature=0.1 for high determinism.
        """
        start_time = time.time()

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            chat_kwargs = {
                "model": self.model,
                "messages": messages,
                "format": "json",
                "options": {
                    "temperature": temperature,
                    "num_predict": 1024
                }
            }
            try:
                response = ollama.chat(**chat_kwargs, think=False)
            except TypeError:
                response = ollama.chat(**chat_kwargs)

            latency = round((time.time() - start_time) * 1000, 2)
            raw_text = ""
            if hasattr(response, "message") and hasattr(response.message, "content"):
                raw_text = response.message.content or ""
            elif isinstance(response, dict):
                raw_text = response.get("message", {}).get("content", "")

            # Parse strictly formatted JSON
            try:
                parsed_data = json.loads(raw_text)
                return GeminiInferenceResult(
                    success=True,
                    data=parsed_data,
                    raw_text=raw_text,
                    provider="ollama_offline",
                    model=self.model,
                    latency_ms=latency
                )
            except json.JSONDecodeError as json_err:
                logger.warning(f"Ollama local model returned invalid JSON: {json_err}. Raw text: {raw_text[:200]}")
                return GeminiInferenceResult(
                    success=False,
                    raw_text=raw_text,
                    provider="ollama_offline",
                    model=self.model,
                    latency_ms=latency,
                    error_message=f"JSON parse error: {str(json_err)}"
                )

        except Exception as err:
            latency = round((time.time() - start_time) * 1000, 2)
            err_str = str(err)
            logger.warning(f"Ollama local inference unavailable or failed: {err_str}. Gracefully falling back to deterministic rules.")
            return GeminiInferenceResult(
                success=False,
                provider="rule_fallback",
                model=self.model,
                latency_ms=latency,
                error_message=err_str,
                is_quota_exhausted=False
            )

# Backward-compatibility alias
OllamaClient = GeminiClient

# Global singleton client instance
_gemini_client_instance = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client_instance
    if _gemini_client_instance is None:
        _gemini_client_instance = GeminiClient()
    return _gemini_client_instance

def get_ollama_client() -> GeminiClient:
    return get_gemini_client()
