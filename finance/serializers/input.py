from rest_framework import serializers
from rest_framework.validators import ValidationError

from accounts.models import User
from core.serializers.fields import DecimalField
from finance.data import currencies
from finance.models import Currency, iSwiftAccount


class RecipientInputSerializer(serializers.Serializer):
    recipient = serializers.UUIDField()
    amount = DecimalField()


class MakeTransferSerializer(serializers.Serializer):
    iswift_account = serializers.UUIDField()
    recipients = serializers.ListField(
        child=RecipientInputSerializer(), min_length=1, required=True
    )
    description = serializers.CharField(required=False, max_length=450)

    def validate_iswift_account(self, value):
        user = self.context["user"]
        try:
            return iSwiftAccount.objects.get(uid=value, user=user)
        except iSwiftAccount.DoesNotExist:
            raise ValidationError("iSwift account does not exist")

    def validate_recipients(self, values):
        users = [value["recipient"] for value in values]
        if len(users) != len(set(users)):
            raise ValidationError("Cannot include the same user more than once")

        validated_users = []
        for value in values:
            try:
                user = User.objects.get(uid=value["recipient"])
                value["recipient"] = user
                validated_users.append(value)

            except User.DoesNotExist:
                # why did I declare the variable?
                # Because Black Formatter was having issues formatting
                # this: {value["recipient"]}
                rec = value["recipient"]
                raise ValidationError(f"User with {rec} is not valid")

        return validated_users

    def validate(self, attrs):
        iswift_account: iSwiftAccount = attrs["iswift_account"]
        recipients = attrs["recipients"]
        total_amount = sum(re["amount"] for re in recipients)
        if iswift_account.balance < total_amount:
            raise ValidationError("Insufficient funds in selected account for transaction")

        return super().validate(attrs)

    def create(self, validated_data):
        iswift_account = validated_data["iswift_account"]
        recipients = validated_data["recipients"]
        description = validated_data["description"]

        debit: str = iswift_account.record_transfer(recipients, description)
        return debit


class CreateAccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, max_length=100)
    currency = serializers.ChoiceField(
        choices=[(key.lower(), value) for key, value in currencies.items()]
    )

    class Meta:
        model = iSwiftAccount
        fields = ["name", "currency", "is_default"]

    def validate_currency(self, value):
        user = self.context["user"]
        try:
            currency = Currency.objects.get(iso_code=value)
        except Currency.DoesNotExist:
            raise ValidationError(f"{value} not in the list of supported currencies")

        if iSwiftAccount.objects.filter(user=user, currency=currency).exists():
            raise ValidationError(f"User already has a {value} account")

        return currency

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user
        is_default = validated_data.pop("is_default", False)

        if "name" not in validated_data:
            validated_data["name"] = f"{validated_data['currency'].iso_code.upper()} Account"

        instance: iSwiftAccount = super().create(validated_data)

        if is_default:
            instance.set_default()

        return instance


class iSwiftAccountUpdateSerializer(serializers.ModelSerializer):
    is_default = serializers.BooleanField(required=False)

    class Meta:
        model = iSwiftAccount
        fields = ["name", "is_default"]

    def update(self, instance: iSwiftAccount, validated_data):
        is_default = validated_data.pop("is_default", None)

        if is_default is not None:
            if is_default:
                instance = instance.set_default()
            else:
                # Check if another account is set as default
                if (
                    not iSwiftAccount.objects.filter(user=instance.user, is_default=True)
                    .exclude(pk=instance.pk)
                    .exists()
                ):
                    raise ValidationError(
                        "Another account must be set as default before unsetting this account."
                    )

        return super().update(instance, validated_data)
