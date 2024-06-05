from rest_framework import serializers


class VerifyOTPPasswordResetSchema(serializers.Serializer):
    uid = serializers.UUIDField()
    token = serializers.CharField()


class KnoxTokenSchema(serializers.Serializer):
    object = serializers.CharField(default="token")
    expiry = serializers.DateTimeField()
    token = serializers.CharField()
