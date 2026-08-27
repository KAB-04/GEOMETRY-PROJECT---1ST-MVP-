from rest_framework import serializers


class SolveSerializer(serializers.Serializer):

    question = serializers.CharField(required=False, allow_blank=False, trim_whitespace=True)

    operation = serializers.CharField(required=False)

    data = serializers.DictField(required=False)

    def validate(self, attrs):

        # AI mode
        if "question" in attrs:
            if len(attrs) != 1:
                raise serializers.ValidationError(
                    "Provide either 'question' or ('operation' and 'data'), not both."
                )
            return attrs

        # Direct solver mode
        if "operation" in attrs and "data" in attrs:
            return attrs

        raise serializers.ValidationError(
            "Provide either 'question' or ('operation' and 'data')."
        )