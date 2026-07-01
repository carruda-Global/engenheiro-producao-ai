import os
import logging
from openai import OpenAI
from src.config import Settings
from src.i18n.translations import get_system_prompt_instruction

logger = logging.getLogger(__name__)

_HF_TOKEN = os.getenv("HF_TOKEN", "")
_HF_MODEL = os.getenv("HF_MODEL", "moonshotai/Kimi-K2-Instruct")
_HF_BASE_URL = "https://router.huggingface.co/v1"


def _make_hf_client() -> OpenAI | None:
    if not _HF_TOKEN:
        return None
    return OpenAI(api_key=_HF_TOKEN, base_url=_HF_BASE_URL, timeout=60)


class DeepSeekClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
            timeout=settings.deepseek_timeout,
        )
        self._hf_client = _make_hf_client()

    def _call(self, client: OpenAI, model: str, messages: list[dict], temperature: float, max_tokens: int) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def _call_with_fallback(self, messages: list[dict], temperature: float, max_tokens: int) -> str:
        """Tenta DeepSeek primeiro; se falhar, usa Kimi-K2 via HF router."""
        try:
            return self._call(self.client, self.settings.deepseek_model, messages, temperature, max_tokens)
        except Exception as e:
            if self._hf_client:
                logger.warning("[LLM] DeepSeek falhou (%s) — usando Kimi-K2 via HF router", e)
                return self._call(self._hf_client, _HF_MODEL, messages, temperature, max_tokens)
            raise

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        lang: str = "pt",
    ) -> str:
        lang_instruction = get_system_prompt_instruction(lang)
        combined_system = f"{system_prompt}\n\n{lang_instruction}"
        messages = [
            {"role": "system", "content": combined_system},
            {"role": "user", "content": user_prompt},
        ]
        return self._call_with_fallback(
            messages,
            temperature or self.settings.deepseek_temperature,
            max_tokens or self.settings.deepseek_max_tokens,
        )

    def chat_with_context(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        lang: str = "pt",
    ) -> str:
        lang_instruction = get_system_prompt_instruction(lang)
        messages = list(messages)
        if messages and messages[0]["role"] == "system":
            messages[0] = {**messages[0], "content": f"{messages[0]['content']}\n\n{lang_instruction}"}
        else:
            messages.insert(0, {"role": "system", "content": lang_instruction})
        return self._call_with_fallback(
            messages,
            temperature or self.settings.deepseek_temperature,
            max_tokens or self.settings.deepseek_max_tokens,
        )

    def health_check(self) -> bool:
        try:
            self.chat(
                system_prompt="Responda apenas: OK",
                user_prompt="Teste de conexao",
                max_tokens=10,
            )
            return True
        except Exception:
            return False
