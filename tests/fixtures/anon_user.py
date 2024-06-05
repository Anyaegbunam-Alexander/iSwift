import pytest
from rest_framework.test import APIClient


@pytest.fixture
def anon_client():
    return APIClient()
