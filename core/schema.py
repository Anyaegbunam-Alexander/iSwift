from rest_framework import serializers


class ResponseDictSchema(serializers.Serializer):
    message = serializers.CharField()


class VerifyOTPPasswordResetSchema(serializers.Serializer):
    uid = serializers.UUIDField()
    token = serializers.CharField()
