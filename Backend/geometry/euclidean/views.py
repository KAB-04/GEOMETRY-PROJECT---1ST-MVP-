from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services import calculate_distance, calculate_circle_area
from .serializers import DistanceSerializer, CircleAreaSerializer


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


@api_view(['POST'])
def circle_area_api(request):
    serializer = CircleAreaSerializer(data=request.data)

    if serializer.is_valid():
        radius = serializer.validated_data['radius']
        result = calculate_circle_area(radius)

        return Response({"area": result}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
