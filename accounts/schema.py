from rest_framework import serializers


class VerifyOTPPasswordResetSchema(serializers.Serializer):
    uid = serializers.UUIDField()
    token = serializers.CharField()
