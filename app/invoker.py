"""HTTP proxy for calling the backend OData system."""

from typing import Any, Dict
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


class BackendInvoker:
    """Thin wrapper around :mod:`requests` with Basic Auth."""

    def __init__(self, base_url: str, username: str, password: str):
        if not base_url:
            raise ValueError("Backend base URL is not configured")
        if not base_url.startswith(("http://", "https://")):
            base_url = "http://" + base_url
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        # Use HTTPBasicAuth so the Authorization header is sent on the
        # first request rather than waiting for a 401 challenge.
        self.session.auth = HTTPBasicAuth(username, password)

    def get(self, path: str, params: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json_data: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=json_data)
        resp.raise_for_status()
        return resp.json()


def create_invoker(base_url: str) -> BackendInvoker:
    """Create an invoker using credentials from ``.env`` or environment."""

    load_dotenv()
    username = os.getenv("USERNAME", os.getenv("ODATA_USERNAME", "user"))
    password = os.getenv("PASSWORD", os.getenv("ODATA_PASSWORD", "password"))
    return BackendInvoker(base_url, username, password)
