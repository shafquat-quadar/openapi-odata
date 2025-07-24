from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from .db import fetch_service, list_active_services
from .parser import parse_metadata
from .models import build_models
from .invoker import create_invoker
from .tool_registry import build_registry
from fastapi.responses import JSONResponse

SERVICE_CACHE: Dict[str, "ServiceContext"] = {}


class ServiceContext:
    def __init__(self, name: str, metadata_xml: str, base_url: str):
        self.name = name
        self.metadata_xml = metadata_xml
        self.base_url = base_url
        self.parsed = parse_metadata(metadata_xml)
        self.models = build_models(self.parsed)
        self.invoker = create_invoker(base_url)
        self.tools = build_registry(name, self.parsed)


def get_context(service: str) -> ServiceContext:
    ctx = SERVICE_CACHE.get(service)
    if not ctx:
        data = fetch_service(service)
        if not data:
            raise HTTPException(404, "Unknown service")
        ctx = ServiceContext(data["name"], data["metadata_xml"], data["base_url"])
        SERVICE_CACHE[service] = ctx
    return ctx


router = APIRouter()


@router.get("/services")
def services() -> Any:
    return list_active_services()


@router.get("/services/{service}/metadata")
def service_metadata(service: str) -> Any:
    ctx = get_context(service)
    return JSONResponse(content=ctx.metadata_xml)


@router.post("/services/{service}/refresh")
def refresh(service: str) -> Any:
    if service in SERVICE_CACHE:
        SERVICE_CACHE.pop(service)
    get_context(service)
    return {"refreshed": True}


@router.get("/tools/{service}")
def tools(service: str) -> Any:
    ctx = get_context(service)
    return ctx.tools


@router.get("/schema/{service}")
def schema(service: str) -> Any:
    ctx = get_context(service)
    entity_models = {
        name: model_info["model"].schema()
        for name, model_info in ctx.models["entities"].items()
    }
    return entity_models


@router.get("/{service}/{entity}")
def list_entities(
    service: str,
    entity: str,
    filter_: Optional[str] = Query(None, alias="$filter"),
    top: Optional[int] = Query(None, alias="$top"),
    skip: Optional[int] = Query(None, alias="$skip"),
    orderby: Optional[str] = Query(None, alias="$orderby"),
    expand: Optional[str] = Query(None, alias="$expand"),
    count: Optional[bool] = Query(None, alias="$count"),
) -> Any:
    ctx = get_context(service)
    if entity not in ctx.models.get("entity_sets", {}):
        raise HTTPException(404, "Unknown entity")
    params: Dict[str, Any] = {}
    if filter_ is not None:
        params["$filter"] = filter_
    if top is not None:
        params["$top"] = top
    if skip is not None:
        params["$skip"] = skip
    if orderby is not None:
        params["$orderby"] = orderby
    if expand is not None:
        params["$expand"] = expand
    if count is not None:
        params["$count"] = str(count).lower()
    return ctx.invoker.get(f"/{service}/{entity}", params)


@router.get("/{service}/{entity}({keys})")
def get_entity(
    service: str,
    entity: str,
    keys: str,
    expand: Optional[str] = Query(None, alias="$expand"),
) -> Any:
    ctx = get_context(service)
    if entity not in ctx.models.get("entity_sets", {}):
        raise HTTPException(404, "Unknown entity")
    params: Dict[str, Any] = {}
    if expand is not None:
        params["$expand"] = expand
    return ctx.invoker.get(f"/{service}/{entity}({keys})", params)


@router.get("/{service}/{entity}({keys})/{nav}")
def navigate(
    service: str,
    entity: str,
    keys: str,
    nav: str,
    filter_: Optional[str] = Query(None, alias="$filter"),
    top: Optional[int] = Query(None, alias="$top"),
    skip: Optional[int] = Query(None, alias="$skip"),
    orderby: Optional[str] = Query(None, alias="$orderby"),
    expand: Optional[str] = Query(None, alias="$expand"),
    count: Optional[bool] = Query(None, alias="$count"),
) -> Any:
    ctx = get_context(service)
    if entity not in ctx.models.get("entity_sets", {}):
        raise HTTPException(404, "Unknown entity")
    params: Dict[str, Any] = {}
    if filter_ is not None:
        params["$filter"] = filter_
    if top is not None:
        params["$top"] = top
    if skip is not None:
        params["$skip"] = skip
    if orderby is not None:
        params["$orderby"] = orderby
    if expand is not None:
        params["$expand"] = expand
    if count is not None:
        params["$count"] = str(count).lower()
    return ctx.invoker.get(f"/{service}/{entity}({keys})/{nav}", params)


@router.post("/invoke/{service}/{function}")
def invoke(service: str, function: str, body: Dict[str, Any]) -> Any:
    ctx = get_context(service)
    return ctx.invoker.post(f"/{service}/{function}", body)
