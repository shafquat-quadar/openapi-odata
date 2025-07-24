import os
from typing import Any, Dict, List, Optional


# Default location for a metadata XML file.  The path can be overridden via the
# ``METADATA_XML_FILE`` environment variable.  ``BASE_URL`` may also be set
# through ``ODATA_BASE_URL`` to control the backend API endpoint.
METADATA_XML_FILE = os.getenv("METADATA_XML_FILE", "sample_metadata.xml")
BASE_URL = os.getenv("ODATA_BASE_URL", "http://example.com")


def fetch_service(service: str) -> Optional[Dict[str, Any]]:
    """Return service configuration loaded from ``METADATA_XML_FILE``."""

    if not os.path.exists(METADATA_XML_FILE):
        return None

    with open(METADATA_XML_FILE, "r", encoding="utf-8") as fh:
        xml_data = fh.read()

    return {
        "id": 1,
        "name": service,
        "metadata_xml": xml_data,
        "base_url": BASE_URL,
    }


def list_active_services() -> List[Dict[str, Any]]:
    """Return the single local service as active."""

    return [
        {
            "name": os.path.splitext(os.path.basename(METADATA_XML_FILE))[0],
            "description": "Local OData service from XML file",
        }
    ]
