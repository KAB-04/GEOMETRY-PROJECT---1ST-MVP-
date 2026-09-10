import json
import math
import re

from .gemini_client import GeminiClient
from .prompt import SYSTEM_PROMPT
from .exceptions import (
    InvalidGeminiResponse,
    GeminiConnectionError,
    ProviderAccessDenied,
    ProviderRateLimited,
    ProviderResponseError,
    ProviderUnavailable,
    ProviderUnreachable,
    UnsupportedGeometryOperation,
)


class ParserService:

    OPERATION_ALIASES = {
        "hypotenuse": "pythagoras",
        "right_triangle_hypotenuse": "pythagoras",
        "circle area": "circle_area",
        "area_of_circle": "circle_area",
        "distance_between_points": "distance",
        "straight_line_distance": "distance",
        "triangle area": "triangle_area",
        "area_of_triangle": "triangle_area",
        "mid_point": "midpoint",
        "missing_triangle_angle": "triangle_third_angle",
        "third_triangle_angle": "triangle_third_angle",
        "third_angle": "triangle_third_angle",
        "triangle_angle_sum": "triangle_third_angle",
    }

    DATA_FIELD_ALIASES = ("data", "parameters", "params", "arguments", "inputs")

    PARAMETER_ALIASES = {
        "circle_area": {
            "radius": "rho",
            "r": "rho",
        },
        "circle_circumference": {
            "radius": "rho",
            "r": "rho",
        },
        "arc_length": {
            "radius": "rho",
            "r": "rho",
            "theta": "theta_rad",
            "angle": "theta_rad",
        },
        "sector_area": {
            "radius": "rho",
            "r": "rho",
            "theta": "theta_rad",
            "angle": "theta_rad",
        },
        "sin_rule": {
            "angle": "alpha_rad",
            "alpha": "alpha_rad",
        },
        "cosine_rule_side": {
            "angle": "alpha_rad",
            "alpha": "alpha_rad",
        },
        "triangle_area": {
            "b": "base",
            "h": "height",
            "perpendicular_height": "height",
        },
        "triangle_third_angle": {
            "a": "angle1",
            "b": "angle2",
            "alpha": "angle1",
            "beta": "angle2",
            "alpha_deg": "angle1",
            "beta_deg": "angle2",
            "first_angle": "angle1",
            "second_angle": "angle2",
        },
        "rectangle_area": {
            "l": "length",
            "w": "width",
        },
        "rectangle_perimeter": {
            "l": "length",
            "w": "width",
        },
    }

    POINT_OPERATIONS = {"distance", "midpoint", "slope"}
    TRANSFORMATION_CUES = re.compile(
        r"\b(reflect(?:ion)?|mirror|translat(?:e|ion)|shift|rotat(?:e|ion)|turn)\b",
        re.IGNORECASE,
    )
    CIRCLE_INTERSECTION_CUES = re.compile(
        r"\bcircles?\b.*\b(intersect|intersection|touch|tangent)\b",
        re.IGNORECASE | re.DOTALL,
    )

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

            operation = self.OPERATION_ALIASES.get(
                self._normalize_operation_name(result["operation"]),
                self._normalize_operation_name(result["operation"]),
            )
            if operation in self.POINT_OPERATIONS and self.TRANSFORMATION_CUES.search(question):
                raise UnsupportedGeometryOperation(
                    "The question requests a geometric transformation, but it was not interpreted as one."
                )
            if operation == "distance" and self.CIRCLE_INTERSECTION_CUES.search(question):
                raise UnsupportedGeometryOperation(
                    "The question requests circle intersection, but it was not interpreted as one."
                )
            return {
                "operation": operation,
                "data": self._normalize_data(operation, result, question),
            }

        except json.JSONDecodeError:

            raise InvalidGeminiResponse(
                "Gemini returned invalid JSON."
            )

        except InvalidGeminiResponse:
            raise

        except UnsupportedGeometryOperation:
            raise

        except (ProviderUnavailable, ProviderUnreachable, ProviderAccessDenied, ProviderRateLimited, ProviderResponseError):
            raise

        except Exception as e:

            raise GeminiConnectionError(str(e))

    @staticmethod
    def _parse_json(response):
        cleaned = response.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if fenced:
            cleaned = fenced.group(1)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Some model versions add a short preamble despite the JSON mode.
            start = cleaned.find("{")
            if start < 0:
                raise
            result, _ = json.JSONDecoder().raw_decode(cleaned[start:])
            return result

    @staticmethod
    def _normalize_operation_name(operation):
        return operation.strip().lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def _normalize_data(cls, operation, result, question=""):
        raw_data = None
        for field in cls.DATA_FIELD_ALIASES:
            if field in result:
                raw_data = result[field]
                break

        if raw_data is None:
            raise InvalidGeminiResponse("Gemini response is missing a data field.")
        if not isinstance(raw_data, dict):
            raise InvalidGeminiResponse("Gemini response data must be an object.")

        if operation in {"distance3d", "midpoint3d", "vector3d", "triangle3d", "plane3d"}:
            return cls._normalize_3d_data(raw_data)
        if operation == "transform":
            return cls._normalize_transform_data(raw_data)

        if operation == "circle_circle_intersection":
            raw_data = cls._complete_circle_intersection_data(raw_data, question)

        raw_data = cls._normalize_point_data(operation, raw_data)
        aliases = cls.PARAMETER_ALIASES.get(operation, {})
        normalized = {}
        for key, value in raw_data.items():
            normalized_key = cls._normalize_parameter_name(key)
            normalized_key = aliases.get(normalized_key, normalized_key)
            if normalized_key.endswith("_deg"):
                normalized_key = f"{normalized_key[:-4]}_rad"
                value = math.radians(cls._normalize_number(value))

            normalized[normalized_key] = cls._normalize_number(value)

        if operation == "circle_circle_intersection":
            normalized = {key: normalized[key] for key in ("x1", "y1", "r1", "x2", "y2", "r2") if key in normalized}

        return normalized

    @classmethod
    def _normalize_3d_data(cls, raw_data):
        points = raw_data.get("points")
        if not isinstance(points, list):
            raise InvalidGeminiResponse("3-D operations require a points list.")
        normalized = {"points": []}
        for point in points:
            if not isinstance(point, dict) or not isinstance(point.get("id"), str):
                raise InvalidGeminiResponse("Each 3-D point requires an id, x, y, and z.")
            values = {axis: cls._normalize_number(point.get(axis)) for axis in ("x", "y", "z")}
            if not all(isinstance(values[axis], (int, float)) for axis in values):
                raise InvalidGeminiResponse("3-D point coordinates must be numeric.")
            normalized["points"].append({"id": point["id"], **values})
        return normalized

    @classmethod
    def _complete_circle_intersection_data(cls, raw_data, question):
        if all(key in raw_data for key in ("x1", "y1", "r1", "x2", "y2", "r2")):
            return raw_data
        centers = re.findall(
            r"center\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)",
            question,
            re.IGNORECASE,
        )
        radii = re.findall(
            r"radius\s*(?:of|=)?\s*(-?\d+(?:\.\d+)?)",
            question,
            re.IGNORECASE,
        )
        completed = dict(raw_data)
        if len(centers) >= 2:
            completed.setdefault("x1", float(centers[0][0]))
            completed.setdefault("y1", float(centers[0][1]))
            completed.setdefault("x2", float(centers[1][0]))
            completed.setdefault("y2", float(centers[1][1]))
        if len(radii) >= 2:
            completed.setdefault("r1", float(radii[0]))
            completed.setdefault("r2", float(radii[1]))
        return completed

    @classmethod
    def _normalize_transform_data(cls, raw_data):
        points = raw_data.get("points")
        if not isinstance(points, list) or not points:
            raise InvalidGeminiResponse("Transformation data must contain a non-empty points list.")
        normalized = {
            "transformation": str(raw_data.get("transformation", "")).strip(),
            "points": [],
        }
        if not normalized["transformation"]:
            raise InvalidGeminiResponse("Transformation data is missing its transformation type.")
        for point in points:
            if not isinstance(point, dict) or not isinstance(point.get("id"), str):
                raise InvalidGeminiResponse("Each transformation point must contain an id, x, and y.")
            x = cls._normalize_number(point.get("x"))
            y = cls._normalize_number(point.get("y"))
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise InvalidGeminiResponse("Transformation point coordinates must be numeric.")
            normalized["points"].append({"id": point["id"], "x": x, "y": y})
        identifiers = [point["id"] for point in normalized["points"]]
        if len(identifiers) != len(set(identifiers)):
            raise InvalidGeminiResponse("Transformation point IDs must be unique.")
        for key in ("dx", "dy"):
            if key in raw_data:
                normalized[key] = cls._normalize_number(raw_data[key])
        return normalized

    @classmethod
    def _normalize_point_data(cls, operation, raw_data):
        if operation not in cls.POINT_OPERATIONS:
            return raw_data

        point1 = (
            raw_data.get("point1")
            or raw_data.get("p1")
            or raw_data.get("from")
            or raw_data.get("start")
            or raw_data.get("A")
            or raw_data.get("a")
        )
        point2 = (
            raw_data.get("point2")
            or raw_data.get("p2")
            or raw_data.get("to")
            or raw_data.get("end")
            or raw_data.get("B")
            or raw_data.get("b")
        )

        points = raw_data.get("points")
        if (point1 is None or point2 is None) and isinstance(points, list) and len(points) >= 2:
            point1, point2 = points[0], points[1]

        if point1 is None or point2 is None:
            return raw_data

        first = cls._point_to_xy(point1)
        second = cls._point_to_xy(point2)
        if first is None or second is None:
            return raw_data

        normalized = {
            key: value
            for key, value in raw_data.items()
            if key not in {"point1", "point2", "p1", "p2", "from", "to", "start", "end", "A", "B", "a", "b", "points"}
        }
        normalized.update(
            {
                "x1": first[0],
                "y1": first[1],
                "x2": second[0],
                "y2": second[1],
            }
        )
        return normalized

    @classmethod
    def _point_to_xy(cls, point):
        if isinstance(point, dict):
            x = point.get("x")
            y = point.get("y")
            if x is None or y is None:
                return None
            return cls._normalize_number(x), cls._normalize_number(y)

        if isinstance(point, (list, tuple)) and len(point) >= 2:
            return cls._normalize_number(point[0]), cls._normalize_number(point[1])

        return None

    @staticmethod
    def _normalize_parameter_name(parameter):
        return str(parameter).strip().lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _normalize_number(value):
        if not isinstance(value, str):
            return value

        stripped = value.strip()
        try:
            return int(stripped)
        except ValueError:
            try:
                return float(stripped)
            except ValueError:
                return value
