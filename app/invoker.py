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
        try:
            return resp.json()
        except ValueError:
            # Some endpoints may return plain text or XML. In that case just
            # return the raw text so FastAPI can pass it through.
            return resp.text

    def post(self, path: str, json_data: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=json_data)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text


def create_invoker(base_url: str) -> BackendInvoker:
    """Create an invoker using credentials from ``.env`` or environment."""

    # Allow the .env file to override existing environment variables so that
    # USERNAME/PASSWORD defined by the operating system don't take precedence.
    load_dotenv(override=True)
    # ``ODATA_USERNAME`` and ``ODATA_PASSWORD`` take priority over the more
    # generic ``USERNAME``/``PASSWORD`` variables.
    username = os.getenv("ODATA_USERNAME") or os.getenv("USERNAME")
    password = os.getenv("ODATA_PASSWORD") or os.getenv("PASSWORD")
    if not username or not password:
        raise ValueError("Backend credentials are not configured")
    return BackendInvoker(base_url, username, password)
