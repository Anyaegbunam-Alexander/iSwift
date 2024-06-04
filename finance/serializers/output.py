from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers.output import PublicUserSerializer
from core.serializers.output import ModelBaseSerializer
from finance.models import CreditTransaction, Currency, DebitTransaction, iSwiftAccount


class CurrencySerializer(ModelBaseSerializer):
    class Meta:
        model = Currency
        fields = ["uid", "name", "iso_code"]


class iSwiftAccountSerializer(ModelBaseSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = iSwiftAccount
        fields = ["uid", "name", "currency", "balance", "is_default"]


class CreditTransactionSerializer(ModelBaseSerializer):
    currency_sent = CurrencySerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = CreditTransaction
        fields = [
            "uid",
            "user",
            "description",
            "sender",
            "amount_sent",
            "currency_sent",
        ]

    @extend_schema_field(PublicUserSerializer)
    def get_user(self, obj):
        return PublicUserSerializer(obj.iswift_account.user).data


class DebitTransactionSerializer(ModelBaseSerializer):
    currency = CurrencySerializer()
    iswift_account = iSwiftAccountSerializer()
    recipients = serializers.SerializerMethodField()

    class Meta:
        model = DebitTransaction
        fields = [
            "uid",
            "iswift_account",
            "description",
            "currency",
            "recipients",
            "amount_sent",
        ]

    @extend_schema_field(CreditTransactionSerializer(many=True))
    def get_recipients(self, obj):
        serializer = CreditTransactionSerializer(obj.credit_transactions.all(), many=True)
        return serializer.data


class PrivateCreditTransactionSerializer(CreditTransactionSerializer):
    iswift_account = iSwiftAccountSerializer()
    currency_received = CurrencySerializer()

    class Meta(CreditTransactionSerializer.Meta):
        fields = CreditTransactionSerializer.Meta.fields + [
            "iswift_account",
            "amount_received",
            "currency_received",
        ]


class iSwiftAccountDetailSerializer(iSwiftAccountSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta(iSwiftAccountSerializer.Meta):
        fields = iSwiftAccountSerializer.Meta.fields + ["transactions"]

    def get_transactions(self, obj):
        return None
