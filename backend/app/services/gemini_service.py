"""Gemini model integration service."""

from functools import lru_cache

import google.generativeai as genai

from app.core.config import settings


class GeminiServiceError(Exception):
	"""Raised when Gemini generation fails."""


@lru_cache(maxsize=1)
def get_gemini_model() -> genai.GenerativeModel:
	api_key = (settings.gemini_api_key or "").strip()
	if not api_key:
		raise GeminiServiceError("GEMINI_API_KEY is not configured")

	try:
		genai.configure(api_key=api_key)
		return genai.GenerativeModel(settings.gemini_model)
	except Exception as exc:
		raise GeminiServiceError("Failed to initialize Gemini model") from exc


def generate_answer(
	system_prompt: str,
	user_prompt: str,
	temperature: float | None = None,
) -> str:
	model = get_gemini_model()
	temp = settings.temperature if temperature is None else temperature

	try:
		response = model.generate_content(
			[
				{"role": "user", "parts": [f"System Instructions:\n{system_prompt}"]},
				{"role": "user", "parts": [user_prompt]},
			],
			generation_config={"temperature": temp},
		)
	except Exception as exc:
		raise GeminiServiceError("Gemini API request failed") from exc

	text = (getattr(response, "text", None) or "").strip()
	if text:
		return text

	raise GeminiServiceError("Gemini returned an empty response")

