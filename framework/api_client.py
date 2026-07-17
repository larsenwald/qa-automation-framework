"""Thin wrapper over requests for the ShopLite REST API."""
import requests


class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip("/") + "/api"
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        self.timeout = timeout

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, self.base_url + path, **kwargs)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    # -- auth -----------------------------------------------------------------
    def login(self, username, password):
        resp = self.post("/auth/token", json={"username": username, "password": password})
        resp.raise_for_status()
        self.session.headers["Authorization"] = f"Bearer {resp.json()['token']}"
        return self

    def logout(self):
        self.session.headers.pop("Authorization", None)
        return self
