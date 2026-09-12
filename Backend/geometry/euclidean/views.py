import math
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SolveSerializer

from .solver.Solver import Solver
from .solver.planner import SolutionPlanner
from .solver.exceptions import (
    InvalidParametersError,
    OperationNotFoundError,
    SolverError,
)
from .solver.Solver import INVALID_GEOMETRY_PARAMETERS_MESSAGE
from .explanations import build_explanation, operation_label
from .parser.exceptions import (
    ParserError,
    ProviderAccessDenied,
    ProviderRateLimited,
    ProviderResponseError,
    ProviderUnavailable,
    ProviderUnreachable,
)
from .parser.exceptions import UnsupportedGeometryOperation
from .parser.parser_service import ParserService

solver = Solver()
solution_planner = SolutionPlanner(solver)
parser_service = None
logger = logging.getLogger(__name__)


@api_view(["GET"])
def health_api(request):
    return Response({"success": True, "status": "ok"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def solve_api(request):
    serializer = SolveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"success": False, "error": {"code": "invalid_request", "details": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST,
        )

    validated_data = serializer.validated_data
    question = validated_data.get("question")

    try:
        if question is not None:
            global parser_service
            if parser_service is None:
                parser_service = ParserService()
            parsed = parser_service.parse(question)
            if parsed.get("semantic_problem"):
                planned = solution_planner.solve(parsed["semantic_problem"])
                logger.info(
                    "Semantic plan geometry_type=%s dimension=%s requested=%s produced=%s request_satisfied=%s visualization=%s/%s",
                    planned["semantic_problem"].get("geometry_type"),
                    planned["semantic_problem"].get("dimension"),
                    planned["semantic_problem"].get("requested"),
                    list(planned["result"].keys()) if isinstance(planned["result"], dict) else [planned["operation"]],
                    True,
                    planned["semantic_problem"].get("geometry_type"),
                    planned["semantic_problem"].get("dimension"),
                )
                operation = planned["operation"]
                data = planned["data"]
                result = planned["result"]
            else:
                operation = parsed["operation"]
                data = parsed["data"]
                result = solver.solve(operation, data)
        else:
            operation = ParserService.OPERATION_ALIASES.get(
                ParserService._normalize_operation_name(validated_data["operation"]),
                ParserService._normalize_operation_name(validated_data["operation"]),
            )
            data = ParserService._normalize_data(operation, {"data": validated_data["data"]})
            semantic_problem = ParserService._semantic_problem_from_interpretation(operation, data, "")
            if semantic_problem:
                planned = solution_planner.solve(semantic_problem)
                operation = planned["operation"]
                data = planned["data"]
                result = planned["result"]
            else:
                result = solver.solve(operation, data)

        explanation = build_explanation(operation, data, result, question)
        return Response(
            {
                "success": True,
                "question": question,
                "operation": operation,
                "operation_label": operation_label(operation),
                "result": result,
                "explanation": explanation,
                "visualization": _visualization_for(operation, data, result, question),
            },
            status=status.HTTP_200_OK,
        )
    except OperationNotFoundError as exc:
        return Response(
            {"success": False, "error": {"code": "UNSUPPORTED_GEOMETRY_OPERATION", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except UnsupportedGeometryOperation as exc:
        return Response(
            {"success": False, "error": {"code": "UNSUPPORTED_GEOMETRY_OPERATION", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ProviderUnreachable as exc:
        logger.warning("AI provider unreachable: %s", exc, exc_info=True)
        return Response(
            {"success": False, "error": {"code": "AI_PROVIDER_UNREACHABLE", "message": "The geometry interpretation service could not be reached. Please try again shortly."}},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except ProviderUnavailable as exc:
        logger.warning("AI provider temporarily unavailable: %s", exc, exc_info=True)
        return Response(
            {"success": False, "error": {"code": "AI_PROVIDER_UNAVAILABLE", "message": "The geometry interpretation service is temporarily busy. Please try again shortly."}},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except ProviderAccessDenied as exc:
        logger.warning("AI provider access denied: %s", exc, exc_info=True)
        return Response(
            {"success": False, "error": {"code": "AI_PROVIDER_ACCESS_DENIED", "message": "The geometry interpretation service rejected access. Check the provider account or network restrictions."}},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except ProviderRateLimited as exc:
        logger.warning("AI provider rate limited: %s", exc, exc_info=True)
        return Response(
            {"success": False, "error": {"code": "AI_PROVIDER_RATE_LIMITED", "message": "The geometry interpretation service is temporarily rate-limited. Please try again later."}},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    except ProviderResponseError as exc:
        logger.warning("AI provider returned an invalid response: %s", exc, exc_info=True)
        return Response(
            {"success": False, "error": {"code": "AI_PROVIDER_INVALID_RESPONSE", "message": "The geometry interpretation service returned an invalid response. Please try again."}},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except ParserError as exc:
        if question is None:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "INVALID_GEOMETRY_PARAMETERS",
                        "message": INVALID_GEOMETRY_PARAMETERS_MESSAGE,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"success": False, "error": {"code": "parser_error", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidParametersError as exc:
        return Response(
            {
                "success": False,
                "error": {
                    "code": "INVALID_GEOMETRY_PARAMETERS",
                    "message": INVALID_GEOMETRY_PARAMETERS_MESSAGE,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except SolverError as exc:
        return Response(
            {"success": False, "error": {"code": "solver_error", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )


def _visualization_for(operation, data, result=None, question=None):
    if operation in {"distance3d", "midpoint3d", "vector3d", "line3d", "triangle3d", "plane3d", "cuboid_volume", "cylinder_volume", "cylinder_lateral_surface_area", "cylinder_total_surface_area", "cylinder_solution", "cone_solution", "cone_volume", "cone_lateral_surface_area", "cone_total_surface_area", "cone_height_from_radius_slant_height"}:
        return _visualization_3d_for(operation, data, result)
    if operation == "circle_circle_intersection" and isinstance(result, dict):
        final_points = result["final"].get("points", [])
        objects = [
            {"type": "circle", "id": "C1", "center": {"x": data["x1"], "y": data["y1"]}, "radius": data["r1"], "label": "C1"},
            {"type": "circle", "id": "C2", "center": {"x": data["x2"], "y": data["y2"]}, "radius": data["r2"], "label": "C2"},
            {"type": "point", "id": "C1-center", "x": data["x1"], "y": data["y1"], "label": "C1", "coordinateLabel": False},
            {"type": "point", "id": "C2-center", "x": data["x2"], "y": data["y2"], "label": "C2", "coordinateLabel": False},
        ]
        objects.extend(
            {"type": "point", "id": f"P{index + 1}", "x": point["x"], "y": point["y"], "label": f"P{index + 1}", "calculated": True}
            for index, point in enumerate(final_points)
        )
        return {"dimension": "2d", "coordinateSystem": True, "objects": objects}
    if {"x1", "y1", "x2", "y2"}.issubset(data):
        objects = [
            {"type": "point", "id": "A", "x": data["x1"], "y": data["y1"], "label": "A"},
            {"type": "point", "id": "B", "x": data["x2"], "y": data["y2"], "label": "B"},
            {"type": "segment", "from": "A", "to": "B", "label": _length_label(result)},
        ]
        if operation == "midpoint" and isinstance(result, (list, tuple)):
            objects.append({"type": "point", "id": "M", "x": result[0], "y": result[1], "label": "M", "calculated": True})
        return {
            "dimension": "2d",
            "coordinateSystem": True,
            "objects": [
                *objects,
            ],
        }
    if "rho" in data and operation in {"circle_area", "circle_circumference"}:
        return {
            "dimension": "2d",
            "coordinateSystem": False,
            "objects": [
                {"type": "point", "id": "O", "x": 0, "y": 0, "label": "O"},
                {"type": "circle", "id": "circle", "center": {"x": 0, "y": 0}, "radius": data["rho"], "label": f"r = {_format_number(data['rho'])}"},
                {"type": "segment", "from": "O", "to": "R", "label": f"r = {_format_number(data['rho'])}"},
                {"type": "point", "id": "R", "x": data["rho"], "y": 0, "label": "R"},
            ],
        }
    if operation == "triangle_area":
        base, height = data["base"], data["height"]
        return {
            "dimension": "2d",
            "coordinateSystem": False,
            "objects": [
                {"type": "point", "id": "A", "x": 0, "y": 0, "label": "A"},
                {"type": "point", "id": "B", "x": base, "y": 0, "label": "B"},
                {"type": "point", "id": "C", "x": base * 0.35, "y": height, "label": "C"},
                {"type": "polygon", "id": "ABC", "vertices": ["A", "B", "C"]},
                {"type": "segment", "from": "A", "to": "B", "label": f"{_format_number(base)} units"},
                {"type": "segment", "from": "C", "to": "H", "label": f"{_format_number(height)} units", "dashed": True},
                {"type": "point", "id": "H", "x": base * 0.35, "y": 0, "label": "H"},
            ],
        }
    if operation == "triangle_third_angle":
        point_c = _triangle_point_for_angles(data["angle1"], data["angle2"], result)
        return {
            "dimension": "2d",
            "coordinateSystem": False,
            "objects": [
                {"type": "point", "id": "A", "x": 0, "y": 0, "label": "A"},
                {"type": "point", "id": "B", "x": 6, "y": 0, "label": "B"},
                {"type": "point", "id": "C", "x": point_c[0], "y": point_c[1], "label": "C"},
                {"type": "polygon", "id": "ABC", "vertices": ["A", "B", "C"]},
                {"type": "angle", "vertex": "A", "from": "B", "to": "C", "value": data["angle1"]},
                {"type": "angle", "vertex": "B", "from": "A", "to": "C", "value": data["angle2"]},
                {"type": "angle", "vertex": "C", "from": "A", "to": "B", "value": result, "calculated": True},
            ],
        }
    if operation == "pythagoras":
        a, b = data["a"], data["b"]
        return {
            "dimension": "2d",
            "coordinateSystem": False,
            "objects": [
                {"type": "point", "id": "A", "x": 0, "y": 0, "label": "A"},
                {"type": "point", "id": "B", "x": a, "y": 0, "label": "B"},
                {"type": "point", "id": "C", "x": 0, "y": b, "label": "C"},
                {"type": "polygon", "id": "ABC", "vertices": ["A", "B", "C"]},
                {"type": "segment", "from": "A", "to": "B", "label": f"{_format_number(a)} units"},
                {"type": "segment", "from": "A", "to": "C", "label": f"{_format_number(b)} units"},
                {"type": "segment", "from": "B", "to": "C", "label": f"{_format_number(result)} units", "calculated": True},
                {"type": "angle", "vertex": "A", "from": "B", "to": "C", "value": 90},
            ],
        }
    if operation in {"rectangle_area", "rectangle_perimeter"}:
        length, width = data["length"], data["width"]
        return {
            "dimension": "2d",
            "coordinateSystem": False,
            "objects": [
                {"type": "point", "id": "A", "x": 0, "y": 0, "label": "A"},
                {"type": "point", "id": "B", "x": length, "y": 0, "label": "B"},
                {"type": "point", "id": "C", "x": length, "y": width, "label": "C"},
                {"type": "point", "id": "D", "x": 0, "y": width, "label": "D"},
                {"type": "polygon", "id": "ABCD", "vertices": ["A", "B", "C", "D"]},
                {"type": "segment", "from": "A", "to": "B", "label": f"{_format_number(length)} units"},
                {"type": "segment", "from": "B", "to": "C", "label": f"{_format_number(width)} units"},
            ],
        }
    if operation == "transform" and isinstance(result, dict):
        original = result.get("original", [])
        transformed = result.get("transformed", [])
        objects = [
            {"type": "point", **point, "variant": "original", "coordinateLabel": False}
            for point in original
        ] + [
            {"type": "point", **point, "variant": "transformed", "coordinateLabel": False}
            for point in transformed
        ]
        if len(original) >= 3:
            objects.append({"type": "polygon", "id": "original", "vertices": [point["id"] for point in original], "variant": "original"})
        if len(transformed) >= 3:
            objects.append({"type": "polygon", "id": "transformed", "vertices": [point["id"] for point in transformed], "variant": "transformed"})
        objects.extend(
            {"type": "segment", "from": source["id"], "to": target["id"], "dashed": True, "variant": "correspondence"}
            for source, target in zip(original, transformed)
        )
        return {"dimension": "2d", "coordinateSystem": True, "objects": objects}
    return {"dimension": "2d", "objects": []}


def _visualization_3d_for(operation, data, result):
    objects = []
    points = data.get("points", [])
    objects.extend({"type": "point3d", **point, "label": point["id"]} for point in points)
    if operation == "distance3d":
        objects.append({"type": "segment3d", "from": points[0]["id"], "to": points[1]["id"], "label": _length_label(result)})
    elif operation == "midpoint3d":
        objects.append({"type": "point3d", "id": "M", **{axis: result[axis] for axis in ("x", "y", "z")}, "label": "M", "calculated": True})
        objects.append({"type": "segment3d", "from": points[0]["id"], "to": points[1]["id"], "label": "AB"})
    elif operation == "vector3d" and isinstance(result, dict):
        objects.append({"type": "vector3d", "from": result["from"], "to": result["to"], "label": "v"})
    elif operation == "line3d" and isinstance(result, dict):
        objects.append({"type": "line3d", "through": result["through"], "label": "line"})
    elif operation == "triangle3d" and isinstance(result, dict):
        objects.append({"type": "triangle3d", "vertices": result["vertices"]})
    elif operation == "plane3d" and isinstance(result, dict):
        objects.append({"type": "plane", "points": points, "normal": result["normal"], "label": "plane"})
    elif operation == "cuboid_volume":
        objects.append({
            "type": "cuboid",
            "origin": [0, 0, 0],
            "width": data["width"],
            "height": data["height"],
            "depth": data["depth"],
            "labels": {
                "width": f"w = {_format_number(data['width'])}",
                "height": f"h = {_format_number(data['height'])}",
                "depth": f"d = {_format_number(data['depth'])}",
            },
        })
    elif operation in {"cylinder_volume", "cylinder_lateral_surface_area", "cylinder_total_surface_area"}:
        objects.append({
            "type": "cylinder",
            "origin": [0, 0, 0],
            "radius": data["radius"],
            "height": data["height"],
            "label": "Cylinder",
            "labels": {
                "radius": f"r = {_format_number(data['radius'])}",
                "height": f"h = {_format_number(data['height'])}",
            },
        })
    elif operation in {"cone_solution", "cone_volume", "cone_lateral_surface_area", "cone_total_surface_area", "cone_height_from_radius_slant_height"}:
        objects.append({
            "type": "cone",
            "origin": [0, 0, 0],
            "radius": data["radius"],
            "height": data["height"],
            "slantHeight": data.get("slant_height"),
            "label": "Cone",
            "labels": {
                "radius": f"r = {_format_number(data['radius'])}",
                "height": f"h = {_format_number(data['height'])}",
                "slantHeight": f"l = {_format_number(data['slant_height'])}" if data.get("slant_height") is not None else None,
            },
        })
    return {"dimension": "3d", "coordinateSystem": True, "objects": objects}


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _length_label(value):
    return f"{_format_number(value)} units" if value is not None else None


def _triangle_point_for_angles(angle_a, angle_b, angle_c):
    sine_c = math.sin(math.radians(angle_c))
    if math.isclose(sine_c, 0):
        return 0.5, 1
    side_ac = 6 * math.sin(math.radians(angle_b)) / sine_c
    return side_ac * math.cos(math.radians(angle_a)), side_ac * math.sin(math.radians(angle_a))

