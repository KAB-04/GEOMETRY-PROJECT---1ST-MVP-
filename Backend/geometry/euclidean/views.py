from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .SolveSerializer import SolveSerializer

from .solver.Solver import Solver
from .solver.exceptions import (
    OperationNotFoundError,
    SolverError,
)

solver = Solver()


@api_view(['POST'])
def solve_api(request):
    serializer = SolveSerializer(data=request.data)

    if serializer.is_valid():

        operation = serializer.validated_data['operation']
        data = serializer.validated_data['data']

        try:
            result = solver.solve(operation, data)

            return Response(
                {"result": result},
                status=status.HTTP_200_OK
            )

        except OperationNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        except SolverError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )