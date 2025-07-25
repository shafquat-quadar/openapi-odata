"""Simple JSON-RPC 2.0 server exposing OData endpoints."""
import sys
from typing import Optional
from jsonrpcserver import method, dispatch

from openapi_server.routes.odata import (
    services as _services,
    metadata as _metadata,
    get_entity as _get_entity,
    list_entities as _list_entities,
    invoke as _invoke,
    call_function as _call_function,
)


@method
def services() -> list:
    return _services()


@method
def metadata(service: str) -> object:
    return _metadata(service)


@method
def get_entity(service: str, entity: str, keys: str, expand: Optional[str] = None) -> object:
    return _get_entity(service, entity, keys, expand)


@method
def list_entities(
    service: str,
    entity: str,
    filter_: Optional[str] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    orderby: Optional[str] = None,
    expand: Optional[str] = None,
    count: Optional[bool] = None,
) -> object:
    return _list_entities(service, entity, filter_, top, skip, orderby, expand, count)


@method
def invoke(service: str, path: str, method: str = "GET", json: Optional[dict] = None) -> object:
    return _invoke({"service": service, "path": path, "method": method, "json": json})


@method
def call_function(service: str, name: str, body: dict) -> object:
    return _call_function(service, name, body)


def serve() -> None:
    """Run the JSON-RPC server reading from stdin and writing to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = dispatch(line)
        if response.wanted:
            print(response, flush=True)
