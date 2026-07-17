import pytest

from tests.api import schemas

pytestmark = pytest.mark.api


def test_issue_token(api, assert_schema):
    resp = api.post("/auth/token", json={"username": "qa_lead", "password": "Passw0rd!"})
    assert resp.status_code == 200
    assert_schema(resp.json(), schemas.TOKEN)


@pytest.mark.parametrize("payload", [
    {"username": "qa_lead", "password": "wrong"},
    {"username": "ghost", "password": "Passw0rd!"},
    {"username": "qa_lead"},
    {},
])
def test_bad_credentials_rejected(api, assert_schema, payload):
    resp = api.post("/auth/token", json=payload)
    assert resp.status_code == 401
    assert_schema(resp.json(), schemas.ERROR)


def test_non_json_body_rejected(api):
    resp = api.post("/auth/token", data="username=qa_lead&password=Passw0rd!")
    assert resp.status_code == 401


@pytest.mark.parametrize("header, message", [
    (None, "Missing bearer token"),
    ("Token abc", "Missing bearer token"),
    ("Bearer not-a-real-token", "Invalid token"),
])
def test_protected_endpoints_require_valid_token(api, header, message):
    headers = {"Authorization": header} if header else {}
    resp = api.get("/cart", headers=headers)
    assert resp.status_code == 401
    assert resp.json()["error"] == message


def test_tampered_token_rejected(base_url, api):
    good = api.post("/auth/token", json={"username": "qa_lead", "password": "Passw0rd!"}).json()["token"]
    tampered = good[:-2] + ("AA" if not good.endswith("AA") else "BB")
    resp = api.get("/cart", headers={"Authorization": f"Bearer {tampered}"})
    assert resp.status_code == 401
