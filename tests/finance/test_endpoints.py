from random import choice
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

from accounts.models import User
from finance.models import Currency
from tests.fixtures.finance import CurrencyFixtures

pytestmark = pytest.mark.django_db


class TestGetCurrencies(CurrencyFixtures):

    @pytest.mark.finance
    def test_get_currencies(self, anon_client: APIClient):
        response: Response = anon_client.get(reverse("finance:list_currencies"))
        assert response.status_code == 200
        assert response.data


class TestListUsers:
    @pytest.mark.finance
    def test_list_users(self, auth_client, user_factory):
        [user_factory() for _ in range(10)]
        response: Response = auth_client.get(reverse("finance:list_users"))
        assert response.status_code == 200
        assert response.data["results"]


class TestMakeTransfer(CurrencyFixtures):
    @pytest.mark.finance
    def test_make_single_transfer_success(self, auth_user_client, iswift_account_factory):
        user, client = auth_user_client
        recipient_acc = iswift_account_factory()
        sender_acc = iswift_account_factory(user=user)
        data = {
            "recipients": [{"recipient": recipient_acc.user.uid, "amount": 1000}],
            "iswift_account": sender_acc.uid,
        }
        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 201
        assert response.data

    @pytest.mark.finance
    def test_make_bulk_transfer_success(self, auth_user_client, iswift_account_factory):
        user, client = auth_user_client
        recipients = [iswift_account_factory() for i in range(5)]
        sender_acc = iswift_account_factory(user=user)
        data = {
            "recipients": [
                {"recipient": recipient.user.uid, "amount": 1000} for recipient in recipients
            ],
            "iswift_account": sender_acc.uid,
        }
        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 201
        assert response.data

    @pytest.mark.finance
    def test_make_transfer_fail_insufficient_balance(
        self, auth_user_client, iswift_account_factory
    ):
        user, client = auth_user_client
        recipient_acc = iswift_account_factory()
        sender_acc = iswift_account_factory(user=user)
        data = {
            "recipients": [{"recipient": recipient_acc.user.uid, "amount": 99_999_999}],
            "iswift_account": sender_acc.uid,
        }
        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 400

    @pytest.mark.finance
    def test_make_transfer_fail_nonexistent_user(self, auth_user_client, iswift_account_factory):
        user, client = auth_user_client
        sender_acc = iswift_account_factory(user=user)
        data = {
            "recipients": [{"recipient": uuid4(), "amount": 1000}],
            "iswift_account": sender_acc.uid,
        }
        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 400

    @pytest.mark.finance
    def test_make_transfer_fail_nonexistent_account(
        self, auth_user_client, iswift_account_factory
    ):
        _, client = auth_user_client
        recipient_acc = iswift_account_factory()
        data = {
            "recipients": [{"recipient": recipient_acc.user.uid, "amount": 1000}],
            "iswift_account": uuid4(),
        }
        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 404

    @pytest.mark.finance
    def test_make_transfer_fail_same_account_operation(
        self, auth_user_client, iswift_account_factory
    ):
        user, client = auth_user_client
        sender_acc = iswift_account_factory(user=user)
        data = {
            "recipients": [{"recipient": sender_acc.user.uid, "amount": 1000}],
            "iswift_account": sender_acc.uid,
        }

        response: Response = client.post(reverse("finance:transfer"), data=data)
        assert response.status_code == 403


class TestiSwiftAccountsListCreate(CurrencyFixtures):
    @pytest.mark.finance
    def test_list_iswift_account(self, auth_user_with_iswift_accounts: tuple[User, APIClient]):
        accounts, client = auth_user_with_iswift_accounts
        response: Response = client.get(reverse("finance:iswift_accounts"))
        assert response.status_code == 200
        assert len(response.data) == len(accounts)

    @pytest.mark.finance
    def test_create_iswift_account_success(self, auth_user_client):
        user, client = auth_user_client
        existing_usr_acc = user.iswift_accounts.all()
        pks = [i.pk for i in existing_usr_acc]
        currencies = Currency.objects.exclude(pk__in=pks)
        data = {
            "name": "Test name",
            "currency": choice(currencies).iso_code,
            "is_default": True,
        }
        response: Response = client.post(reverse("finance:iswift_accounts"), data=data)
        assert response.status_code == 201

        user_accs = user.iswift_accounts.filter(is_default=True)
        assert user_accs.count() == 1
        assert str(user_accs.first().uid) == response.data["uid"]


class TestiSwiftAccountDetail(CurrencyFixtures):
    @pytest.mark.finance
    def test_get_one_iswift_account(
        self, auth_user_client, debit_transaction_factory, credit_transaction_factory
    ):
        user, client = auth_user_client
        user_acc = user.iswift_accounts.first()
        response: Response = client.get(
            reverse("finance:one_iswift_account", kwargs={"uid": user_acc.uid})
        )
        assert response.status_code == 200
        assert not response.data["transactions"]

        credit_transaction_factory(iswift_account=user_acc)
        debit_transaction_factory(iswift_account=user_acc)
        response: Response = client.get(
            reverse("finance:one_iswift_account", kwargs={"uid": user_acc.uid})
        )
        assert response.status_code == 200
        assert response.data["transactions"]

    @pytest.mark.finance
    def test_update_one_iswift_account_success(self, auth_user_client):
        user, client = auth_user_client
        user_acc = user.iswift_accounts.first()
        data = {"name": "Updated Name"}
        response: Response = client.post(
            reverse("finance:one_iswift_account", kwargs={"uid": user_acc.uid}), data=data
        )
        assert response.status_code == 200
        assert response.data["name"] == data["name"]

    @pytest.mark.finance
    def test_update_iswift_account_raises_validation_error_without_default_account(
        self, auth_user_client
    ):
        user, client = auth_user_client
        user_acc = user.iswift_accounts.first()
        data = {"is_default": False}
        response: Response = client.post(
            reverse("finance:one_iswift_account", kwargs={"uid": user_acc.uid}), data=data
        )
        assert response.status_code == 400


class TestTransactionDetail(CurrencyFixtures):
    @pytest.mark.finance
    @pytest.mark.parametrize(
        "t_type, transaction_factory",
        [
            ("credit-transaction", "credit_transaction_factory"),
            ("debit-transaction", "debit_transaction_factory"),
        ],
    )
    def test_get_one_transaction_success(
        self, request, auth_user_client, t_type, transaction_factory
    ):
        user, client = auth_user_client
        transaction = request.getfixturevalue(transaction_factory)(iswift_account__user=user)
        response: Response = client.get(
            reverse("finance:one_transaction", kwargs={"uid": transaction.uid, "type": t_type})
        )
        assert response.status_code == 200

    def test_get_one_transaction_fail_invalid_type(
        self, auth_user_client, credit_transaction_factory
    ):
        user, client = auth_user_client
        transaction = credit_transaction_factory(iswift_account__user=user)
        response: Response = client.get(
            reverse("finance:one_transaction", kwargs={"uid": transaction.uid, "type": "invalid"})
        )
        assert response.status_code == 400

    def test_get_one_transaction_fail_not_found(self, auth_client):
        response: Response = auth_client.get(
            reverse(
                "finance:one_transaction", kwargs={"uid": uuid4(), "type": "credit-transaction"}
            )
        )
        assert response.status_code == 404
