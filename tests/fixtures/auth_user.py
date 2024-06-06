import pytest
from rest_framework.test import APIClient


@pytest.fixture
def auth_client(user_factory):
    client = APIClient()
    client.force_authenticate(user_factory())
    return client


@pytest.fixture
def auth_user_client(user_factory, iswift_account_factory):
    client = APIClient()
    user = user_factory()
    iswift_account_factory(user=user, is_default=True)
    client.force_authenticate(user)
    return user, client


@pytest.fixture
def auth_user_with_iswift_accounts(user_factory, iswift_account_factory):
    client = APIClient()
    user = user_factory()
    accounts = [iswift_account_factory(user=user, is_default=False) for _ in range(3)]
    accounts[0].is_default = True
    accounts[0].save()
    client.force_authenticate(user)
    return accounts, client
