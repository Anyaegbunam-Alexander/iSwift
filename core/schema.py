from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers


class ResponseDictSchema(serializers.Serializer):
    message = serializers.CharField()


def uid_parameter(name):
    return OpenApiParameter(
        name="uid",
        type=OpenApiTypes.UUID,
        location=OpenApiParameter.PATH,
        description=f"The uid of the {name}",
    )
