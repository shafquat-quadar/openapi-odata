import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = "shared.sqlite"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def fetch_service(service: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute(
        "SELECT id, name, metadata_xml, base_url FROM services WHERE active=1 AND name=?",
        (service,),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "metadata_xml": row[2], "base_url": row[3]}
    return None


def list_active_services() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.execute(
        "SELECT name, description FROM services WHERE active=1 ORDER BY name"
    )
    res = [{"name": r[0], "description": r[1]} for r in cur.fetchall()]
    conn.close()
    return res
