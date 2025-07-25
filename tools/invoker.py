"""HTTP proxy for backend OData calls."""

from __future__ import annotations

from typing import Any, Dict, Optional
import logging
import requests
from requests.auth import HTTPBasicAuth

from config import settings


class ODataInvoker:
    def __init__(self, base_url: str) -> None:
        if not base_url:
            raise ValueError("Backend base URL missing")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if settings.user and settings.password:
            self.session.auth = HTTPBasicAuth(settings.user, settings.password)
        self.logger = logging.getLogger(__name__)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        self.logger.info(
            "HTTP %s %s params=%s json=%s", method.upper(), url, params, json
        )
        resp = self.session.request(method.upper(), url, params=params, json=json)
        self.logger.info("Status %s", resp.status_code)
        self.logger.debug("Body %s", resp.text)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", path, json=json)
