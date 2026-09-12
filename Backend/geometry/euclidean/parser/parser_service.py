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
        "distance_3d": "distance3d",
        "3d_distance": "distance3d",
        "midpoint_3d": "midpoint3d",
        "3d_midpoint": "midpoint3d",
        "vector_3d": "vector3d",
        "3d_vector": "vector3d",
        "line_3d": "line3d",
        "3d_line": "line3d",
        "triangle_3d": "triangle3d",
        "3d_triangle": "triangle3d",
        "plane_3d": "plane3d",
        "3d_plane": "plane3d",
        "triangle area": "triangle_area",
        "area_of_triangle": "triangle_area",
        "mid_point": "midpoint",
        "missing_triangle_angle": "triangle_third_angle",
        "third_triangle_angle": "triangle_third_angle",
        "third_angle": "triangle_third_angle",
        "triangle_angle_sum": "triangle_third_angle",
        "volume_of_cylinder": "cylinder_volume",
        "cylinder volume": "cylinder_volume",
        "cylinder_surface_area": "cylinder_total_surface_area",
        "surface_area_of_cylinder": "cylinder_total_surface_area",
        "total_cylinder_surface_area": "cylinder_total_surface_area",
        "cylinder_curved_surface_area": "cylinder_lateral_surface_area",
        "curved_surface_area_of_cylinder": "cylinder_lateral_surface_area",
        "cylinder_lateral_area": "cylinder_lateral_surface_area",
        "lateral_area_of_cylinder": "cylinder_lateral_surface_area",
        "height_of_cone": "cone_height_from_radius_slant_height",
        "cone_height": "cone_height_from_radius_slant_height",
        "cone_altitude": "cone_height_from_radius_slant_height",
        "volume_of_cone": "cone_volume",
        "cone volume": "cone_volume",
        "cone_surface_area": "cone_total_surface_area",
        "surface_area_of_cone": "cone_total_surface_area",
        "total_cone_surface_area": "cone_total_surface_area",
        "cone_curved_surface_area": "cone_lateral_surface_area",
        "curved_surface_area_of_cone": "cone_lateral_surface_area",
        "cone_lateral_area": "cone_lateral_surface_area",
        "lateral_area_of_cone": "cone_lateral_surface_area",
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
        "cylinder_volume": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
        },
        "cylinder_lateral_surface_area": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
        },
        "cylinder_total_surface_area": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
        },
        "cone_height_from_radius_slant_height": {
            "r": "radius",
            "rho": "radius",
            "l": "slant_height",
            "slant": "slant_height",
        },
        "cone_volume": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
            "l": "slant_height",
            "slant": "slant_height",
        },
        "cone_lateral_surface_area": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
            "l": "slant_height",
            "slant": "slant_height",
        },
        "cone_total_surface_area": {
            "r": "radius",
            "rho": "radius",
            "h": "height",
            "l": "slant_height",
            "slant": "slant_height",
        },
    }

    POINT_OPERATIONS = {"distance", "midpoint", "slope"}
    CYLINDER_OPERATIONS = {"cylinder_volume", "cylinder_lateral_surface_area", "cylinder_total_surface_area"}
    CONE_OPERATIONS = {"cone_height_from_radius_slant_height", "cone_volume", "cone_lateral_surface_area", "cone_total_surface_area"}
    TRANSFORMATION_CUES = re.compile(
        r"\b(reflect(?:ion)?|mirror|translat(?:e|ion)|shift|rotat(?:e|ion)|turn)\b",
        re.IGNORECASE,
    )
    CIRCLE_INTERSECTION_CUES = re.compile(
        r"\bcircles?\b.*\b(intersect|intersection|touch|tangent)\b",
        re.IGNORECASE | re.DOTALL,
    )
    CYLINDER_CUES = re.compile(r"\bcylinders?\b", re.IGNORECASE)
    CONE_CUES = re.compile(r"\bcones?\b", re.IGNORECASE)
    CYLINDER_VOLUME_CUES = re.compile(r"\b(volume|capacity|v)\b", re.IGNORECASE)
    CYLINDER_TOTAL_SURFACE_CUES = re.compile(r"\b(total\s+surface\s+area|surface\s+area)\b", re.IGNORECASE)
    CYLINDER_LATERAL_SURFACE_CUES = re.compile(r"\b(lateral|curved)\s+(?:surface\s+)?area\b", re.IGNORECASE)
    HEIGHT_CUES = re.compile(r"\b(height|altitude|vertical\s+height|h)\b", re.IGNORECASE)
    DANGEROUS_3D_TO_2D_CUES = re.compile(
        r"\b(cones?|cylinders?|spheres?|cuboids?|cubes?|3[-\s]?d|three[-\s]?dimensional)\b",
        re.IGNORECASE,
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
            operation = self._correct_supported_semantic_operation(operation, question)
            if operation in {"circle_area", "circle_circumference", "rectangle_area", "rectangle_perimeter", "triangle_area", "triangle_perimeter", "distance", "midpoint", "slope"} and self.DANGEROUS_3D_TO_2D_CUES.search(question):
                raise UnsupportedGeometryOperation(
                    "The question requests a 3-D geometry operation, but it was interpreted as a related 2-D operation."
                )
            data = self._normalize_data(operation, result, question)
            response = {"operation": operation, "data": data}
            semantic_problem = self._semantic_problem_from_interpretation(operation, data, question)
            if semantic_problem:
                response["semantic_problem"] = semantic_problem
            return response

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
    def _correct_supported_semantic_operation(cls, operation, question):
        if cls.CONE_CUES.search(question):
            if cls.CYLINDER_LATERAL_SURFACE_CUES.search(question):
                return "cone_lateral_surface_area"
            if cls.CYLINDER_TOTAL_SURFACE_CUES.search(question):
                return "cone_total_surface_area"
            if cls.CYLINDER_VOLUME_CUES.search(question):
                return "cone_volume"
            if cls.HEIGHT_CUES.search(question):
                return "cone_height_from_radius_slant_height"
            return operation
        if not cls.CYLINDER_CUES.search(question):
            return operation
        if cls.CYLINDER_LATERAL_SURFACE_CUES.search(question):
            return "cylinder_lateral_surface_area"
        if cls.CYLINDER_TOTAL_SURFACE_CUES.search(question):
            return "cylinder_total_surface_area"
        if cls.CYLINDER_VOLUME_CUES.search(question):
            return "cylinder_volume"
        return operation

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

        if operation in {"distance3d", "midpoint3d", "vector3d", "line3d", "triangle3d", "plane3d"}:
            return cls._normalize_3d_data(operation, raw_data, question)
        if operation == "transform":
            return cls._normalize_transform_data(raw_data)

        if operation == "circle_circle_intersection":
            raw_data = cls._complete_circle_intersection_data(raw_data, question)
        if operation in cls.CYLINDER_OPERATIONS:
            raw_data = cls._complete_cylinder_data(raw_data, question)
        if operation in cls.CONE_OPERATIONS:
            raw_data = cls._complete_cone_data(raw_data, question)

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
        if operation in cls.CYLINDER_OPERATIONS:
            normalized = {key: normalized[key] for key in ("radius", "height") if key in normalized}
        if operation in cls.CONE_OPERATIONS:
            normalized = {key: normalized[key] for key in ("radius", "height", "slant_height") if key in normalized}

        return normalized

    @classmethod
    def _complete_cylinder_data(cls, raw_data, question):
        completed = dict(raw_data)
        if "radius" not in completed and "r" not in completed and "diameter" not in completed:
            radius = re.search(r"\bradius\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if radius:
                completed["radius"] = cls._normalize_number(radius.group(1))
        if "height" not in completed and "h" not in completed:
            height = re.search(r"\bheight\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if height:
                completed["height"] = cls._normalize_number(height.group(1))
        if "diameter" not in completed:
            diameter = re.search(r"\bdiameter\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if diameter:
                completed["diameter"] = cls._normalize_number(diameter.group(1))
        if "radius" not in completed and "r" not in completed and "diameter" in completed:
            diameter_value = cls._normalize_number(completed["diameter"])
            if isinstance(diameter_value, (int, float)):
                completed["radius"] = diameter_value / 2
        return completed

    @classmethod
    def _complete_cone_data(cls, raw_data, question):
        completed = dict(raw_data)
        if "radius" not in completed and "r" not in completed and "diameter" not in completed:
            radius = re.search(r"\bradius\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if radius:
                completed["radius"] = cls._normalize_number(radius.group(1))
        if "height" not in completed and "h" not in completed:
            height = re.search(r"(?<!slant\s)\b(?:vertical\s+)?height\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if height:
                completed["height"] = cls._normalize_number(height.group(1))
        if "slant_height" not in completed and "l" not in completed:
            slant = re.search(
                r"\b(?:slant\s+height|sloping\s+edge)\b(?:\s+of\s+(?:a\s+)?cone)?\s*(?:=|is|measures)?\s*(-?\d+(?:\.\d+)?)",
                question,
                re.IGNORECASE,
            )
            if slant:
                completed["slant_height"] = cls._normalize_number(slant.group(1))
        if "diameter" not in completed:
            diameter = re.search(r"\bdiameter\s*(?:of|=|is)?\s*(-?\d+(?:\.\d+)?)", question, re.IGNORECASE)
            if diameter:
                completed["diameter"] = cls._normalize_number(diameter.group(1))
        if "radius" not in completed and "r" not in completed and "diameter" in completed:
            diameter_value = cls._normalize_number(completed["diameter"])
            if isinstance(diameter_value, (int, float)):
                completed["radius"] = diameter_value / 2
        return completed

    @classmethod
    def _semantic_problem_from_interpretation(cls, operation, data, question):
        if cls.CONE_CUES.search(question) or operation in cls.CONE_OPERATIONS:
            return {
                "geometry_type": "cone",
                "dimension": "3d",
                "given": {key: data[key] for key in ("radius", "height", "slant_height") if key in data},
                "requested": cls._requested_cone_outputs(question, operation),
            }
        if cls.CYLINDER_CUES.search(question) or operation in cls.CYLINDER_OPERATIONS:
            return {
                "geometry_type": "cylinder",
                "dimension": "3d",
                "given": {key: data[key] for key in ("radius", "height") if key in data},
                "requested": cls._requested_cylinder_outputs(question, operation),
            }
        return None

    @classmethod
    def _requested_cone_outputs(cls, question, operation):
        requested = []
        if cls.HEIGHT_CUES.search(question) or operation == "cone_height_from_radius_slant_height":
            requested.append("height")
        if cls.CYLINDER_VOLUME_CUES.search(question) or operation == "cone_volume":
            requested.append("volume")
        if cls.CYLINDER_LATERAL_SURFACE_CUES.search(question) or operation == "cone_lateral_surface_area":
            requested.append("lateral_surface_area")
        if cls.CYLINDER_TOTAL_SURFACE_CUES.search(question) or operation == "cone_total_surface_area":
            requested.append("total_surface_area")
        return requested

    @classmethod
    def _requested_cylinder_outputs(cls, question, operation):
        requested = []
        if cls.CYLINDER_VOLUME_CUES.search(question) or operation == "cylinder_volume":
            requested.append("volume")
        if cls.CYLINDER_LATERAL_SURFACE_CUES.search(question) or operation == "cylinder_lateral_surface_area":
            requested.append("lateral_surface_area")
        if cls.CYLINDER_TOTAL_SURFACE_CUES.search(question) or operation == "cylinder_total_surface_area":
            requested.append("total_surface_area")
        return requested

    @classmethod
    def _normalize_3d_data(cls, operation, raw_data, question=""):
        points = cls._extract_3d_points(raw_data)
        if len(points) < cls._required_3d_point_count(operation):
            points = cls._extract_3d_points_from_question(question) or points

        required_count = cls._required_3d_point_count(operation)
        if len(points) < required_count:
            raise InvalidGeminiResponse(f"3-D operations require at least {required_count} valid points.")

        normalized = {"points": []}
        for index, point in enumerate(points[:required_count]):
            normalized["points"].append(cls._normalize_3d_point(point, index))
        return normalized

    @classmethod
    def _extract_3d_points(cls, raw_data):
        candidates = []
        points = raw_data.get("points")
        if isinstance(points, list):
            candidates.extend(points)

        for key in ("point1", "p1", "from", "start", "A", "a"):
            if key in raw_data:
                candidates.append(raw_data[key])
                break
        for key in ("point2", "p2", "to", "end", "B", "b"):
            if key in raw_data:
                candidates.append(raw_data[key])
                break
        for key in ("point3", "p3", "C", "c"):
            if key in raw_data:
                candidates.append(raw_data[key])
                break

        if all(key in raw_data for key in ("x1", "y1", "z1")):
            candidates.append({"id": "A", "x": raw_data["x1"], "y": raw_data["y1"], "z": raw_data["z1"]})
        if all(key in raw_data for key in ("x2", "y2", "z2")):
            candidates.append({"id": "B", "x": raw_data["x2"], "y": raw_data["y2"], "z": raw_data["z2"]})
        if all(key in raw_data for key in ("x3", "y3", "z3")):
            candidates.append({"id": "C", "x": raw_data["x3"], "y": raw_data["y3"], "z": raw_data["z3"]})

        return candidates

    @classmethod
    def _normalize_3d_point(cls, point, index):
        point_id = chr(ord("A") + index)
        if isinstance(point, dict):
            if isinstance(point.get("id"), str) and point["id"].strip():
                point_id = point["id"].strip()
            values = [point.get(axis) for axis in ("x", "y", "z")]
        elif isinstance(point, (list, tuple)):
            if len(point) != 3:
                raise InvalidGeminiResponse("3-D point arrays must contain exactly three coordinates.")
            values = list(point)
        else:
            raise InvalidGeminiResponse("Each 3-D point must be an object or a three-coordinate array.")

        coordinates = [cls._coerce_numeric_coordinate(value) for value in values]
        return {"id": point_id, "x": coordinates[0], "y": coordinates[1], "z": coordinates[2]}

    @staticmethod
    def _coerce_numeric_coordinate(value):
        if isinstance(value, bool):
            raise InvalidGeminiResponse("3-D point coordinates must be numeric.")
        if isinstance(value, (int, float)):
            return value
        if not isinstance(value, str):
            raise InvalidGeminiResponse("3-D point coordinates must be numeric.")

        stripped = value.strip()
        if not re.fullmatch(r"-?(?:\d+(?:\.\d*)?|\.\d+)", stripped):
            raise InvalidGeminiResponse("3-D point coordinates must be numeric.")
        return ParserService._normalize_number(stripped)

    @staticmethod
    def _required_3d_point_count(operation):
        if operation in {"triangle3d", "plane3d"}:
            return 3
        return 2

    @classmethod
    def _extract_3d_points_from_question(cls, question):
        if not question:
            return []
        number = r"-?\d+(?:\.\d+)?"
        pattern = re.compile(
            rf"(?:\b(?:point\s+)?(?P<label>[A-Z])\b[^\(\n]{{0,40}})?\(\s*(?P<x>{number})\s*,\s*(?P<y>{number})\s*,\s*(?P<z>{number})\s*\)"
        )
        points = []
        for index, match in enumerate(pattern.finditer(question)):
            label = match.group("label") or chr(ord("A") + index)
            points.append(
                {
                    "id": label,
                    "x": cls._normalize_number(match.group("x")),
                    "y": cls._normalize_number(match.group("y")),
                    "z": cls._normalize_number(match.group("z")),
                }
            )
        return points

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
