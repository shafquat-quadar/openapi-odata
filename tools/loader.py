"""Load OData metadata from file directory or SQLite database."""

from __future__ import annotations

import os
import sqlite3
from typing import List, Tuple

from config import settings


def _load_from_file(service_name: str) -> Tuple[str, str]:
    if not settings.dir:
        raise FileNotFoundError("Metadata directory not configured")
    path = os.path.join(settings.dir, f"{service_name}.xml")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as fh:
        xml = fh.read()
    return xml, ""


def _load_from_db(service_name: str) -> Tuple[str, str]:
    conn = sqlite3.connect(settings.db)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT base_url, metadata_raw FROM odata_services WHERE service_name = ?",
        (service_name,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise FileNotFoundError(f"Service {service_name} not found")
    return row["metadata_raw"], row["base_url"]


def load_metadata(service_name: str) -> Tuple[str, str]:
    if settings.dir:
        return _load_from_file(service_name)
    return _load_from_db(service_name)


def list_services() -> List[str]:
    if settings.dir:
        if not os.path.isdir(settings.dir):
            return []
        return sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(settings.dir)
            if f.lower().endswith(".xml")
        )
    conn = sqlite3.connect(settings.db)
    cur = conn.execute("SELECT service_name FROM odata_services ORDER BY service_name")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows
