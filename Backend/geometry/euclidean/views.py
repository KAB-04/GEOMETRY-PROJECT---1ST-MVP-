from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from Math_Engine.Euclidean_1 import calculate_distance
from .serializers import DistanceSerializer


@api_view(['POST'])
def distance_api(request):
    serializer = DistanceSerializer(data=request.data)

    if serializer.is_valid():
        data = serializer.validated_data

        result = calculate_distance(
            data['x1'],
            data['y1'],
            data['x2'],
            data['y2']
        )

        return Response({"distance": result}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)