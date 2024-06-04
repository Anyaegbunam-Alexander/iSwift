from rest_framework import serializers

from core import object_kebab_case


class ModelBaseSerializer(serializers.ModelSerializer):
    # Base serializer for all serializers.\n
    # This will add the `object` field which is the class name of the
    # object being serialized.
    # It also sorts the fields with uid and object as the first two
    # fields and the rest in alphabetical order

    class Meta:
        fields = ["object"]

    object = serializers.SerializerMethodField()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        try:
            fields: list = cls.Meta.fields
            fields.sort()
            if "uid" in fields:
                fields.remove("uid")
                fields.insert(0, "uid")
                fields.insert(1, "object")
            else:
                fields.insert(0, "object")

        except Exception:
            pass

    def get_object(self, obj) -> str:
        return object_kebab_case(obj)
