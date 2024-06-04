from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers.output import PublicUserSerializer
from core import object_kebab_case
from core.serializers.fields import DecimalField
from core.serializers.output import ModelBaseSerializer
from finance.models import CreditTransaction, Currency, DebitTransaction, iSwiftAccount


class CurrencySerializer(ModelBaseSerializer):
    class Meta:
        model = Currency
        fields = ["uid", "name", "iso_code"]


class iSwiftAccountSerializer(ModelBaseSerializer):
    currency = CurrencySerializer()
    balance = DecimalField()

    class Meta:
        model = iSwiftAccount
        fields = ["uid", "name", "currency", "balance", "is_default"]


class CreditTransactionSerializer(ModelBaseSerializer):
    currency_sent = CurrencySerializer()
    amount_sent = DecimalField()
    sender = PublicUserSerializer()
    # user = serializers.SerializerMethodField()

    class Meta:
        model = CreditTransaction
        fields = [
            "uid",
            "description",
            "sender",
            "amount_sent",
            "currency_sent",
            # "user",
        ]

    @extend_schema_field(PublicUserSerializer)
    def get_user(self, obj):
        return PublicUserSerializer(obj.iswift_account.user).data


class DebitTransactionSerializer(ModelBaseSerializer):
    currency = CurrencySerializer()
    iswift_account = iSwiftAccountSerializer()
    recipients = serializers.SerializerMethodField()
    amount_sent = DecimalField()

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
    amount_received = DecimalField()

    class Meta(CreditTransactionSerializer.Meta):
        fields = CreditTransactionSerializer.Meta.fields + [
            "iswift_account",
            "amount_received",
            "currency_received",
        ]


class TransactionSerializer(serializers.Serializer):
    uid = serializers.UUIDField()
    object = serializers.CharField()
    amount = DecimalField()
    currency = CurrencySerializer()
    description = serializers.CharField(max_length=500)
    sender_or_recipient = serializers.CharField(max_length=101)
    iswift_account = serializers.UUIDField()


class iSwiftAccountDetailSerializer(iSwiftAccountSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta(iSwiftAccountSerializer.Meta):
        fields = iSwiftAccountSerializer.Meta.fields + ["transactions"]

    @extend_schema_field(TransactionSerializer(many=True))
    def get_transactions(self, obj):
        credit_transactions: QuerySet[CreditTransaction] = obj.credit_transactions.select_related(
            "currency_received", "sender"
        ).all()
        debit_transactions: QuerySet[DebitTransaction] = obj.debit_transactions.select_related(
            "currency", "recipient"
        ).all()

        credit_object = object_kebab_case(CreditTransaction())
        debit_object = object_kebab_case(DebitTransaction())

        all_transactions = [
            {
                "iswift_account": credit.iswift_account.uid,
                "amount": credit.amount_received,
                "uid": credit.uid,
                "object": credit_object,
                "currency": CurrencySerializer(credit.currency_received).data,
                "sender_or_recipient": credit.sender.get_full_name(),
                "description": credit.description,
            }
            for credit in credit_transactions
        ] + [
            {
                "iswift_account": debit.iswift_account.uid,
                "uid": debit.uid,
                "object": debit_object,
                "currency": CurrencySerializer(debit.currency).data,
                "sender_or_recipient": (
                    debit.recipient.get_full_name() if debit.recipient else "Bulk Transfer"
                ),
                "amount": debit.amount_sent,
                "description": debit.description,
            }
            for debit in debit_transactions
        ]

        return TransactionSerializer(all_transactions, many=True).data
