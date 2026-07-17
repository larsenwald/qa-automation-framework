import pytest
from jsonschema import validate

from framework.api_client import ApiClient


@pytest.fixture
def api(base_url):
    return ApiClient(base_url)


@pytest.fixture
def auth_api(base_url):
    return ApiClient(base_url).login("qa_lead", "Passw0rd!")


@pytest.fixture
def assert_schema():
    def check(payload, schema):
        validate(instance=payload, schema=schema)
        return payload
    return check
