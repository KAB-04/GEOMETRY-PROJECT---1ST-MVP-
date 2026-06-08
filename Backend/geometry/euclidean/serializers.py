from rest_framework import serializers

class DistanceSerializer(serializers.Serializer):
    x1 = serializers.FloatField()
    y1 = serializers.FloatField()
    x2 = serializers.FloatField()
    y2 = serializers.FloatField()


class CircleAreaSerializer(serializers.Serializer):
    radius = serializers.FloatField()