from functools import lru_cache

from google import genai
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeminiSettings(BaseSettings):
    gemini_api_key: SecretStr
    gemini_model: str = "gemini-3.5-flash-lite"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_gemini_settings() -> GeminiSettings:
    return GeminiSettings()


@lru_cache
def get_gemini_client() -> genai.Client:
    settings = get_gemini_settings()
    return genai.Client(api_key=settings.gemini_api_key.get_secret_value())


async def generate_text(prompt: str) -> tuple[str, str, str]:
    settings = get_gemini_settings()
    client = get_gemini_client()

    response = await client.aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )

    return response.response_id, settings.gemini_model, response.text or ""
