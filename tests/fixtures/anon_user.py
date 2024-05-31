import pytest
from rest_framework.test import APIClient


@pytest.fixture
def anon_user_api_client():
    return APIClient()
