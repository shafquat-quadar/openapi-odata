"""HTTP proxy for calling the backend OData system."""

from typing import Any, Dict
import os
import requests
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
        self.session.auth = (username, password)

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
    username = os.getenv("USERNAME") or os.getenv("ODATA_USERNAME")
    password = os.getenv("PASSWORD") or os.getenv("ODATA_PASSWORD")
    if not username or not password:
        raise ValueError("Backend credentials are not configured")
    return BackendInvoker(base_url, username, password)
