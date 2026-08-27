import json
import re

from .gemini_client import GeminiClient
from .prompt import SYSTEM_PROMPT
from .exceptions import (
    InvalidGeminiResponse,
    GeminiConnectionError,
)


class ParserService:

    def __init__(self):
        try:
            self.client = GeminiClient()
        except ValueError as exc:
            raise GeminiConnectionError(str(exc)) from exc

    def parse(self, question):

        prompt = f"""
{SYSTEM_PROMPT}

User Question:
{question}
"""

        try:

            response = self.client.generate(prompt)

            result = self._parse_json(response)

            if not isinstance(result, dict):
                raise InvalidGeminiResponse("Gemini response must be a JSON object.")
            if not isinstance(result.get("operation"), str) or not result["operation"].strip():
                raise InvalidGeminiResponse("Gemini response is missing an operation.")
            if not isinstance(result.get("data"), dict):
                raise InvalidGeminiResponse("Gemini response is missing an object-valued data field.")

            return result

        except json.JSONDecodeError:

            raise InvalidGeminiResponse(
                "Gemini returned invalid JSON."
            )

        except InvalidGeminiResponse:
            raise

        except Exception as e:

            raise GeminiConnectionError(str(e))

    @staticmethod
    def _parse_json(response):
        cleaned = response.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fenced:
            cleaned = fenced.group(1)
        return json.loads(cleaned)