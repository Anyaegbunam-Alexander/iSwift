import pytest
from rest_framework.test import APIClient


@pytest.fixture
def auth_client(user_factory):
    client = APIClient()
    client.force_authenticate(user_factory())
    return client


@pytest.fixture
def auth_user_client(user_factory):
    client = APIClient()
    user = user_factory()
    client.force_authenticate(user)
    return user, client
