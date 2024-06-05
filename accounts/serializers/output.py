from accounts.models import User
from accounts.schema import KnoxTokenSchema
from core.serializers.output import ModelBaseSerializer


class UserSerializer(ModelBaseSerializer):

    class Meta:
        model = User
        fields = [
            "uid",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "date_joined",
        ]


class PublicUserSerializer(ModelBaseSerializer):
    class Meta:
        model = User
        fields = [
            "uid",
            "first_name",
            "last_name",
            "phone_number",
        ]


class UserLoginSerializer(UserSerializer):
    authentication = KnoxTokenSchema()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["authentication"]
