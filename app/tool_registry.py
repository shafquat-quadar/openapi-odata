from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def generate_spec(app: FastAPI) -> dict:
    return get_openapi(title="MCP OData Bridge", version="1.0.0", routes=app.routes)
