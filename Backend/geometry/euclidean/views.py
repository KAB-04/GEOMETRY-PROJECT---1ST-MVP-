from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .SolveSerializer import SolveSerializer
from .engine_loader import load_all_functions

FUNCTIONS = load_all_functions()


@api_view(['POST'])
def solve_api(request):
    serializer = SolveSerializer(data=request.data)

    if serializer.is_valid():
        operation = serializer.validated_data['operation']
        data = serializer.validated_data['data']

        if operation not in FUNCTIONS:
            return Response(
                {"error": f"{operation} not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = FUNCTIONS[operation](**data)
            return Response({"result": result})

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)