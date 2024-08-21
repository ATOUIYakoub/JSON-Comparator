from rest_framework import serializers

class JSONSerializer(serializers.Serializer):
    json1 = serializers.JSONField()
    json2 = serializers.JSONField()
