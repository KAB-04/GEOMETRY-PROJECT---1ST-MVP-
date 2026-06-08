from rest_framework import serializers


class SolveSerializer(serializers.Serializer):
    operation = serializers.CharField()
    data = serializers.DictField()
