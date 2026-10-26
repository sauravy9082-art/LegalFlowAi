import json
import httpx
import logging
from typing import Dict, Any, Optional
from pydantic import ValidationError

from app.core.config import settings
from app.services.ai_provider import AIProvider

logger = logging.getLogger(__name__)

FALLBACK_ERROR_MESSAGE = "Local AI engine is unavailable. Please start Ollama and verify the selected model."

class OllamaService(AIProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = 25.0 # 25 second max timeout for fast local LLM inference

    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Ollama server is reachable and configured model exists.
        Attempts fallback to 127.0.0.1 if localhost fails.
        """
        urls_to_try = [self.base_url, "http://127.0.0.1:11434", "http://localhost:11434"]
        for target_url in urls_to_try:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.get(f"{target_url.rstrip('/')}/api/tags")
                    if res.status_code == 200:
                        data = res.json()
                        models = [m.get("name") for m in data.get("models", [])]
                        
                        # Auto-adopt installed model if configured model is missing or slightly differs
                        if models:
                            matched = None
                            for m in models:
                                if self.model == m or self.model in m or m.startswith(self.model):
                                    matched = m
                                    break
                            if not matched and any("llama3.2" in m for m in models):
                                matched = next(m for m in models if "llama3.2" in m)
                            if not matched:
                                matched = models[0]
                            self.model = matched

                        self.base_url = target_url.rstrip('/')
                        model_exists = len(models) > 0

                        return {
                            "connected": model_exists,
                            "url": self.base_url,
                            "models": models,
                            "configured_model": self.model,
                            "model_available": model_exists
                        }
            except Exception as e:
                logger.debug(f"Health check attempt to {target_url} failed: {e}")

        return {
            "connected": False,
            "url": self.base_url,
            "models": [],
            "configured_model": self.model,
            "model_available": False
        }

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        health = await self.check_health()
        if not health["connected"]:
            return FALLBACK_ERROR_MESSAGE

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
                else:
                    return f"Ollama HTTP {res.status_code}: {res.text}"
        except Exception as e:
            logger.error(f"Error during Ollama inference: {e}")
            return FALLBACK_ERROR_MESSAGE

    async def generate_json(self, prompt: str, schema_class: Any = None, system_prompt: Optional[str] = None) -> Any:
        if schema_class:
            return await self.generate_structured_json(prompt, schema_class, system_prompt)
        text = await self.generate_text(prompt, system_prompt)
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except Exception:
            return {}

    async def generate_structured_json(
        self,
        prompt: str,
        schema_class: Any,
        system_prompt: Optional[str] = None
    ) -> Any:
        """
        Structured Output generation with schema validation & retry loop (Rule 6).
        """
        health = await self.check_health()
        if not health["connected"]:
            raise RuntimeError(FALLBACK_ERROR_MESSAGE)

        full_system_prompt = (
            (system_prompt + "\n\n" if system_prompt else "") +
            "CRITICAL: You MUST respond ONLY with a valid JSON object matching the required schema. Do not include markdown code blocks (```json), commentary, or introductory text."
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": full_system_prompt,
            "format": "json",
            "stream": False
        }

        # First attempt
        raw_response = ""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    raw_response = res.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama request error: {e}")
            raise RuntimeError(FALLBACK_ERROR_MESSAGE)

        # Parse & Validate
        try:
            parsed_json = json.loads(raw_response)
            return schema_class.model_validate(parsed_json)
        except (json.JSONDecodeError, ValidationError) as err1:
            logger.warning(f"First JSON validation attempt failed: {err1}. Attempting retry prompt.")

        # Retry with Correction Prompt (Rule 6)
        correction_prompt = (
            f"Your previous JSON response was invalid: {raw_response[:200]}...\n\n"
            f"Please generate valid JSON strictly matching this schema format.\n{prompt}"
        )
        payload["prompt"] = correction_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res2 = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res2.status_code == 200:
                    raw_response2 = res2.json().get("response", "").strip()
                    parsed_json2 = json.loads(raw_response2)
                    return schema_class.model_validate(parsed_json2)
        except Exception as err2:
            logger.error(f"Retry structured output failed: {err2}")

        raise ValueError(f"Failed to obtain valid structured JSON output from Ollama model '{self.model}'.")
