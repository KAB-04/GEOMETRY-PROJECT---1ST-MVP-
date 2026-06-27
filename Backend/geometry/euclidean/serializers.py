from rest_framework import serializers


class SolveSerializer(serializers.Serializer):

    question = serializers.CharField(required=False)

    operation = serializers.CharField(required=False)

    data = serializers.DictField(required=False)

    def validate(self, attrs):

        # AI mode
        if "question" in attrs:
            return attrs

        # Direct solver mode
        if "operation" in attrs and "data" in attrs:
            return attrs

        raise serializers.ValidationError(
            "Provide either 'question' or ('operation' and 'data')."
        )