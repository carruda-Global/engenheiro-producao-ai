from openai import OpenAI
from src.config import Settings


class DeepSeekClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_base,
            timeout=settings.deepseek_timeout,
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature or self.settings.deepseek_temperature,
            max_tokens=max_tokens or self.settings.deepseek_max_tokens,
        )
        return response.choices[0].message.content or ""

    def chat_with_context(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=messages,
            temperature=temperature or self.settings.deepseek_temperature,
            max_tokens=max_tokens or self.settings.deepseek_max_tokens,
        )
        return response.choices[0].message.content or ""

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
