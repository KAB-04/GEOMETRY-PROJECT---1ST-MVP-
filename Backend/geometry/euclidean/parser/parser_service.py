import json

from .gemini_client import GeminiClient
from .prompt import SYSTEM_PROMPT
from .exceptions import (
    InvalidGeminiResponse,
    GeminiConnectionError,
)


class ParserService:

    def __init__(self):
        self.client = GeminiClient()

    def parse(self, question):

        prompt = f"""
{SYSTEM_PROMPT}

User Question:
{question}
"""

        try:

            response = self.client.generate(prompt)

            result = json.loads(response)

            return result

        except json.JSONDecodeError:

            raise InvalidGeminiResponse(
                "Gemini returned invalid JSON."
            )

        except Exception as e:

            raise GeminiConnectionError(str(e))