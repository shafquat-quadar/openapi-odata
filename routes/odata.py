from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.loader import load_metadata, list_services
from utils.parser import parse_metadata
from utils.invoker import ODataInvoker
from models.dynamic import build_models


class ServiceContext:
    def __init__(self, name: str) -> None:
        xml, base_url = load_metadata(name)
        self.name = name
        self.metadata_xml = xml
        self.base_url = base_url
        self.parsed = parse_metadata(xml)
        self.models = build_models(self.parsed)
        self.invoker = ODataInvoker(base_url)


CACHE: Dict[str, ServiceContext] = {}


def get_ctx(service: str) -> ServiceContext:
    ctx = CACHE.get(service)
    if not ctx:
        try:
            ctx = ServiceContext(service)
        except FileNotFoundError:
            raise HTTPException(404, "Unknown service")
        CACHE[service] = ctx
    return ctx


router = APIRouter()


@router.get("/services")
def services() -> Any:
    return list_services()


@router.get("/services/{service}/metadata")
def metadata(service: str) -> Any:
    ctx = get_ctx(service)
    return JSONResponse(content=ctx.metadata_xml)


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
    ctx = get_ctx(service)
    if entity not in ctx.models.get("entity_sets", {}):
        raise HTTPException(404, "Unknown entity set")
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
    ctx = get_ctx(service)
    if entity not in ctx.models.get("entity_sets", {}):
        raise HTTPException(404, "Unknown entity set")
    params: Dict[str, Any] = {}
    if expand is not None:
        params["$expand"] = expand
    return ctx.invoker.get(f"/{service}/{entity}({keys})", params)


@router.post("/invoke")
def invoke(data: Dict[str, Any]) -> Any:
    service = data.get("service")
    path = data.get("path")
    method = data.get("method", "GET")
    json_body = data.get("json")
    if not service or not path:
        raise HTTPException(400, "service and path required")
    ctx = get_ctx(service)
    return ctx.invoker.request(method, f"/{service}{path}", json=json_body)


@router.post("/{service}/function/{name}")
def call_function(service: str, name: str, body: Dict[str, Any]) -> Any:
    ctx = get_ctx(service)
    return ctx.invoker.post(f"/{service}/{name}", body)

