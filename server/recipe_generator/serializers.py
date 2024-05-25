from rest_framework import serializers

class AIRequestSerializer(serializers.Serializer):
    input_text = serializers.CharField(max_length=512)

class AIResponseSerializer(serializers.Serializer):
    output_text = serializers.ListField(child=serializers.CharField())
