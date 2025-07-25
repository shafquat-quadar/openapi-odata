from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from utils.loader import load_metadata, list_services
from utils.parser import parse_metadata
from utils.invoker import ODataInvoker
from models.dynamic import build_models


def _quote_value(value: str, edm_type: str) -> str:
    """Quote string values according to their EDM type."""
    if not edm_type.startswith("Edm.String"):
        return value
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        return value
    return f"'{value}'"


def _strip_quotes(value: str) -> str:
    """Remove a matching pair of quotes from the ends of ``value``."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _format_keys(raw_keys: str, key_types: Dict[str, str]) -> str:
    """Ensure key values are correctly quoted based on metadata."""
    if "=" in raw_keys:
        parts = []
        for pair in raw_keys.split(","):
            name, val = pair.split("=", 1)
            name = name.strip()
            val = _strip_quotes(val)
            edm = key_types.get(name, "")
            parts.append(f"{name}={_quote_value(val, edm)}")
        return ",".join(parts)
    # single key
    if key_types:
        name, edm = next(iter(key_types.items()))
        return _quote_value(_strip_quotes(raw_keys), edm)
    return raw_keys


class ServiceContext:
    def __init__(self, name: str) -> None:
        xml, base_url = load_metadata(name)
        self.name = name
        self.metadata_xml = xml
        self.base_url = base_url
        self.parsed = parse_metadata(xml)
        self.models = build_models(self.parsed)
        self.invoker = ODataInvoker(base_url)
        self.key_types = self._extract_key_types()

    def _extract_key_types(self) -> Dict[str, Dict[str, str]]:
        """Map entity set names to their key property EDM types."""
        types: Dict[str, Dict[str, str]] = {}
        et_map = {et["name"]: et for et in self.parsed.get("entity_types", [])}
        for es in self.parsed.get("entity_sets", []):
            et = et_map.get(es.get("entity_type"))
            if not et:
                continue
            key_props = {}
            for prop in et.get("properties", []):
                if prop.get("name") in et.get("keys", []):
                    key_props[prop["name"]] = prop.get("type", "")
            types[es["name"]] = key_props
        return types


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
    formatted = _format_keys(keys, ctx.key_types.get(entity, {}))
    return ctx.invoker.get(f"/{service}/{entity}({formatted})", params)


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

