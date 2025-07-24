"""Database helpers for loading OData service metadata."""

from typing import Any, Dict, List, Optional
import os
import sqlite3


DB_FILE = os.getenv("DB_FILE", "shared.sqlite")
METADATA_SOURCE = os.getenv("METADATA_SOURCE", "db").lower()
METADATA_DIR = os.getenv("METADATA_DIR", "metadata")


def _init_db(conn: sqlite3.Connection) -> None:
    """Ensure the ``services`` table exists."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS services (
            name TEXT PRIMARY KEY,
            description TEXT,
            active INTEGER DEFAULT 1,
            metadata_xml TEXT,
            base_url TEXT
        )
        """
    )
    conn.commit()


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _load_from_dir(service: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(METADATA_DIR, f"{service}.xml")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        xml = fh.read()
    base_url = os.getenv(f"BASE_URL_{service.upper()}", os.getenv("BASE_URL", ""))
    desc = os.getenv(f"DESC_{service.upper()}", "")
    return {
        "name": service,
        "description": desc,
        "metadata_xml": xml,
        "base_url": base_url,
    }


def _list_dir_services() -> List[Dict[str, Any]]:
    if not os.path.isdir(METADATA_DIR):
        return []
    items: List[Dict[str, Any]] = []
    for entry in os.listdir(METADATA_DIR):
        if entry.lower().endswith(".xml"):
            name = os.path.splitext(entry)[0]
            desc = os.getenv(f"DESC_{name.upper()}", "")
            items.append({"name": name, "description": desc})
    return sorted(items, key=lambda x: x["name"])


def fetch_service(service: str) -> Optional[Dict[str, Any]]:
    """Return a service configuration from DB or file directory."""

    if METADATA_SOURCE == "dir":
        return _load_from_dir(service)

    conn = _get_conn()
    cur = conn.execute(
        "SELECT name, description, metadata_xml, base_url FROM services "
        "WHERE name = ? AND active = 1",
        (service,),
    )
    row = cur.fetchone()
    if row:
        return dict(row)
    return None


def list_active_services() -> List[Dict[str, Any]]:
    """Return all active services."""

    if METADATA_SOURCE == "dir":
        return _list_dir_services()

    conn = _get_conn()
    cur = conn.execute(
        "SELECT name, description FROM services WHERE active = 1 ORDER BY name"
    )
    return [dict(r) for r in cur.fetchall()]
