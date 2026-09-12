import os
import json
import logging
import socket
import time
from pathlib import Path
from urllib import error, request

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .exceptions import (
    ProviderAccessDenied,
    ProviderRateLimited,
    ProviderResponseError,
    ProviderUnavailable,
    ProviderUnreachable,
)


BACKEND_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MAX_ATTEMPTS = 3

GEOMETRY_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "operation": {
            "type": "STRING",
            "enum": [
                "distance",
                "circle_area",
                "circle_circumference",
                "circle_circle_intersection",
                "triangle_area",
                "triangle_perimeter",
                "triangle_third_angle",
                "midpoint",
                "slope",
                "rectangle_area",
                "rectangle_perimeter",
                "pythagoras",
                "pythagoras_verify",
                "sin_rule",
                "cosine_rule_side",
                "cosine_rule_angle",
                "transform",
                "distance3d",
                "midpoint3d",
                "vector3d",
                "line3d",
                "triangle3d",
                "plane3d",
                "cuboid_volume",
                "cylinder_volume",
                "cylinder_lateral_surface_area",
                "cylinder_total_surface_area",
                "cone_height_from_radius_slant_height",
                "cone_volume",
                "cone_lateral_surface_area",
                "cone_total_surface_area",
            ],
        },
        "data": {
            "type": "OBJECT",
            "properties": {
                "x1": {"type": "NUMBER"},
                "y1": {"type": "NUMBER"},
                "x2": {"type": "NUMBER"},
                "y2": {"type": "NUMBER"},
                "rho": {"type": "NUMBER"},
                "radius": {"type": "NUMBER"},
                "diameter": {"type": "NUMBER"},
                "r1": {"type": "NUMBER"},
                "r2": {"type": "NUMBER"},
                "base": {"type": "NUMBER"},
                "height": {"type": "NUMBER"},
                "slant_height": {"type": "NUMBER"},
                "l": {"type": "NUMBER"},
                "angle1": {"type": "NUMBER"},
                "angle2": {"type": "NUMBER"},
                "length": {"type": "NUMBER"},
                "width": {"type": "NUMBER"},
                "a": {"type": "NUMBER"},
                "b": {"type": "NUMBER"},
                "c": {"type": "NUMBER"},
                "alpha_rad": {"type": "NUMBER"},
                "transformation": {"type": "STRING"},
                "points": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "x": {"type": "NUMBER"},
                            "y": {"type": "NUMBER"},
                            "z": {"type": "NUMBER"},
                        },
                        "required": ["id", "x", "y", "z"],
                    },
                },
                "point1": {
                    "type": "ARRAY",
                    "items": {"type": "NUMBER"},
                },
                "point2": {
                    "type": "ARRAY",
                    "items": {"type": "NUMBER"},
                },
                "dx": {"type": "NUMBER"},
                "dy": {"type": "NUMBER"},
                "z1": {"type": "NUMBER"},
                "z2": {"type": "NUMBER"},
                "depth": {"type": "NUMBER"},
            },
        },
    },
    "required": ["operation", "data"],
}


class GeminiClient:

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.fallback_enabled = os.getenv("LLM_FALLBACK_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}

        if not self.gemini_api_key and not self.groq_api_key:
            raise ValueError("GEMINI_API_KEY or GROQ_API_KEY not found.")

        self.primary_model = os.getenv("GEMINI_PRIMARY_MODEL") or os.getenv("GEMINI_MODEL")
        self.fallback_model = os.getenv("GEMINI_FALLBACK_MODEL")
        if self.gemini_api_key and not self.primary_model:
            raise ValueError("GEMINI_PRIMARY_MODEL not found.")

        self.client = (
            genai.Client(api_key=self.gemini_api_key)
            if self.gemini_api_key
            else None
        )
        self.groq_model = os.getenv("GROQ_MODEL")
        if not self.gemini_api_key and self.groq_api_key and not self.groq_model:
            raise ValueError("GROQ_MODEL not found.")
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt):
        if self.client is not None:
            try:
                return self._generate_with_gemini_model(prompt, self.primary_model, "primary")
            except ProviderUnavailable as primary_unavailable:
                if self.fallback_model:
                    logger.info("Switching to Gemini secondary model after primary availability failures.")
                    try:
                        return self._generate_with_gemini_model(prompt, self.fallback_model, "secondary")
                    except ProviderUnavailable as secondary_unavailable:
                        if not self.fallback_enabled:
                            raise secondary_unavailable from primary_unavailable
                elif not self.fallback_enabled:
                    raise primary_unavailable
            except Exception as gemini_error:
                provider_error = self._classify_gemini_error(gemini_error)
                if provider_error is not None:
                    raise provider_error from gemini_error
                if not self.fallback_enabled or not self.groq_api_key:
                    raise

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found.")

        return self._generate_with_groq(prompt)

    def _generate_with_gemini_model(self, prompt, model, role):
        gemini_error = None
        for attempt in range(GEMINI_MAX_ATTEMPTS):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GEOMETRY_RESPONSE_SCHEMA,
                    ),
                )
                logger.info("Gemini %s attempt %s succeeded.", role, attempt + 1)
                return response.text
            except Exception as error:
                gemini_error = error
                provider_error = self._classify_gemini_error(error)
                if not isinstance(provider_error, ProviderUnavailable):
                    raise error
                logger.warning("Gemini %s attempt %s returned temporary availability failure.", role, attempt + 1)
                if attempt < GEMINI_MAX_ATTEMPTS - 1:
                    time.sleep(2**attempt)

        raise ProviderUnavailable("Gemini is temporarily busy.") from gemini_error

    @staticmethod
    def _classify_gemini_error(gemini_error):
        message = str(gemini_error).lower()
        status_code = getattr(gemini_error, "code", None) or getattr(gemini_error, "status_code", None)
        if status_code == 503 or "service_unavailable" in message or "unavailable" in message:
            return ProviderUnavailable("Gemini is temporarily busy.")
        if status_code == 429 or "resource_exhausted" in message or "quota exceeded" in message:
            return ProviderRateLimited("Gemini quota limit reached.")
        if status_code in {401, 403} or "permission_denied" in message or "api key" in message and "invalid" in message:
            return ProviderAccessDenied("Gemini rejected access.")
        if "getaddrinfo" in message or "name or service not known" in message or "connection" in message or "timed out" in message:
            return ProviderUnreachable("Gemini could not be reached.")
        return None

    def _generate_with_groq(self, prompt):
        payload = json.dumps(
            {
                "model": self.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")
        http_request = request.Request(
            self.groq_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as groq_error:
            details = groq_error.read().decode("utf-8", errors="replace")
            if groq_error.code in {401, 403}:
                raise ProviderAccessDenied(
                    f"Groq rejected access (HTTP {groq_error.code})."
                ) from groq_error
            if groq_error.code == 429:
                raise ProviderRateLimited("Groq rate limit reached.") from groq_error
            raise RuntimeError(f"Groq request failed ({groq_error.code}): {details}") from groq_error
        except error.URLError as groq_error:
            if isinstance(groq_error.reason, socket.gaierror):
                raise ProviderUnreachable("Groq hostname could not be resolved.") from groq_error
            raise ProviderUnreachable("Groq could not be reached.") from groq_error
        except TimeoutError as groq_error:
            raise ProviderUnreachable("Groq request timed out.") from groq_error

        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as response_error:
            raise ProviderResponseError("Groq returned an invalid response.") from response_error
