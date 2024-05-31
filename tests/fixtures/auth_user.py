import pytest
from rest_framework.test import APIClient


@pytest.fixture
def auth_user_api_client(user_factory):
    client = APIClient()
    client.force_authenticate(user_factory())
    return client
