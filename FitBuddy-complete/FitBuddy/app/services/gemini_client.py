from functools import lru_cache

from google import genai
from google.genai import types

from ..config import get_settings


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot generate a usable response."""


@lru_cache
def get_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_enabled:
        raise GeminiServiceError("Gemini is not enabled.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(
    *,
    model: str,
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.7,
    max_output_tokens: int = 4096,
) -> str:
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction,
        )
        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        text = (response.text or "").strip()
        if not text:
            raise GeminiServiceError("Gemini returned an empty response.")
        return text
    except Exception as exc:
        raise GeminiServiceError(f"Gemini request failed: {exc}") from exc


def generate_structured(
    *,
    model: str,
    prompt: str,
    response_schema,
    system_instruction: str | None = None,
    temperature: float = 0.6,
    max_output_tokens: int = 8192,
):
    """Generate JSON matching a Pydantic model and validate it."""
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system_instruction,
        )
        response = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        if not response.text:
            raise GeminiServiceError("Gemini returned an empty structured response.")
        return response_schema.model_validate_json(response.text)
    except GeminiServiceError:
        raise
    except Exception as exc:
        raise GeminiServiceError(f"Gemini structured request failed: {exc}") from exc
