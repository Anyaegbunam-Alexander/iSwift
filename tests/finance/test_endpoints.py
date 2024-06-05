from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

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
