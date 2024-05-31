from rest_framework import serializers


class ResponseSchema(serializers.Serializer):
    message = serializers.CharField()
