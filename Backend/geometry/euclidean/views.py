from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import SolveSerializer

from .solver.Solver import Solver
from .solver.exceptions import (
    InvalidParametersError,
    OperationNotFoundError,
    SolverError,
)
from .parser.exceptions import ParserError
from .parser.parser_service import ParserService

solver = Solver()
parser_service = None


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
            operation = parsed["operation"]
            data = parsed["data"]
        else:
            operation = validated_data["operation"]
            data = validated_data["data"]

        result = solver.solve(operation, data)
        return Response(
            {
                "success": True,
                "question": question,
                "operation": operation,
                "result": result,
                "explanation": f"Calculated using the {operation} geometry operation.",
                "visualization": _visualization_for(operation, data),
            },
            status=status.HTTP_200_OK,
        )
    except OperationNotFoundError as exc:
        return Response(
            {"success": False, "error": {"code": "unsupported_operation", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ParserError as exc:
        return Response(
            {"success": False, "error": {"code": "parser_error", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidParametersError as exc:
        return Response(
            {"success": False, "error": {"code": "invalid_parameters", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except SolverError as exc:
        return Response(
            {"success": False, "error": {"code": "solver_error", "message": str(exc)}},
            status=status.HTTP_400_BAD_REQUEST,
        )


def _visualization_for(operation, data):
    if {"x1", "y1", "x2", "y2"}.issubset(data):
        return {
            "dimension": "2d",
            "objects": [
                {"type": "point", "id": "A", "x": data["x1"], "y": data["y1"]},
                {"type": "point", "id": "B", "x": data["x2"], "y": data["y2"]},
                {"type": "segment", "from": "A", "to": "B"},
            ],
        }
    if "rho" in data and operation == "circle_area":
        return {
            "dimension": "2d",
            "objects": [{"type": "circle", "id": "circle", "center": {"x": 0, "y": 0}, "radius": data["rho"]}],
        }
    return {"dimension": "2d", "objects": []}

