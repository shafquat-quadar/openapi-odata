from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request
from .db import fetch_service, list_active_services
from .parser import parse_metadata
from .model_builder import build_models
from .invoker import BackendInvoker
from pydantic import BaseModel
from dotenv import load_dotenv
import os

SERVICE_CONTEXTS: Dict[str, "ServiceContext"] = {}


class ServiceContext:
    def __init__(self, name: str, metadata_xml: str, base_url: str):
        self.name = name
        self.metadata_xml = metadata_xml
        self.base_url = base_url
        self.parsed = parse_metadata(metadata_xml)
        self.models = build_models(self.parsed)
        load_dotenv()
        username = os.getenv("ODATA_USERNAME", "user")
        password = os.getenv("ODATA_PASSWORD", "password")
        self.invoker = BackendInvoker(base_url, username, password)


def get_context(service: str) -> ServiceContext:
    ctx = SERVICE_CONTEXTS.get(service)
    if not ctx:
        data = fetch_service(service)
        if not data:
            raise HTTPException(404, "Unknown service")
        ctx = ServiceContext(data["name"], data["metadata_xml"], data["base_url"])
        SERVICE_CONTEXTS[service] = ctx
    return ctx


router = APIRouter()


@router.get("/services")
def get_services():
    return list_active_services()


@router.get("/services/{service}/metadata")
def get_metadata(service: str):
    ctx = get_context(service)
    return ctx.metadata_xml


@router.post("/services/{service}/refresh")
def refresh_service(service: str):
    if service in SERVICE_CONTEXTS:
        SERVICE_CONTEXTS.pop(service)
    get_context(service)
    return {"refreshed": True}


@router.get("/tools/{service}")
def get_tools(service: str, request: Request):
    # The OpenAPI document is generated globally, but agents may filter by service
    from fastapi.openapi.utils import get_openapi
    app = request.app
    return get_openapi(title="MCP OData Bridge", version="1.0.0", routes=app.routes)


@router.get("/{service}/{entity}")
def list_entities(service: str, entity: str, request: Request):
    ctx = get_context(service)
    if entity not in ctx.models:
        raise HTTPException(404, "Unknown entity")
    params = dict(request.query_params)
    return ctx.invoker.get(f"/{entity}", params)


@router.get("/{service}/{entity}({key})")
def get_entity(service: str, entity: str, key: str, request: Request):
    ctx = get_context(service)
    if entity not in ctx.models:
        raise HTTPException(404, "Unknown entity")
    params = dict(request.query_params)
    return ctx.invoker.get(f"/{entity}({key})", params)


@router.get("/{service}/{entity}({key})/{nav}")
def navigate(service: str, entity: str, key: str, nav: str, request: Request):
    ctx = get_context(service)
    if entity not in ctx.models:
        raise HTTPException(404, "Unknown entity")
    params = dict(request.query_params)
    return ctx.invoker.get(f"/{entity}({key})/{nav}", params)


@router.post("/invoke/{service}/{function}")
def invoke_function(service: str, function: str, body: Dict[str, Any]):
    ctx = get_context(service)
    return ctx.invoker.post(f"/{function}", body)
