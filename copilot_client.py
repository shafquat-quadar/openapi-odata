from __future__ import annotations
import os
from dotenv import load_dotenv

class CopilotStudioClient:
    """Simple client loading credentials from a .env file."""

    def __init__(self) -> None:
        # Load variables from .env if present
        load_dotenv()
        self.environment_id = os.getenv("environmentId")
        self.agent_identifier = os.getenv("agentIdentifier")
        self.tenant_id = os.getenv("tenantId")
        self.app_client_id = os.getenv("appClientId")

        missing = [
            name
            for name, val in [
                ("environmentId", self.environment_id),
                ("agentIdentifier", self.agent_identifier),
                ("tenantId", self.tenant_id),
                ("appClientId", self.app_client_id),
            ]
            if not val
        ]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    def __repr__(self) -> str:
        return (
            "CopilotStudioClient("
            f"environment_id={self.environment_id}, "
            f"agent_identifier={self.agent_identifier}, "
            f"tenant_id={self.tenant_id}, "
            f"app_client_id={self.app_client_id})"
        )
