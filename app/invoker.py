import os
from typing import Any, Dict
import requests


class BackendInvoker:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)

    def get(self, path: str, params: Dict[str, Any]):
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json_data: Dict[str, Any]):
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=json_data)
        resp.raise_for_status()
        return resp.json()
