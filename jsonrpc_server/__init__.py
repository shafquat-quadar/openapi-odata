"""Simple JSON-RPC 2.0 server exposing OData endpoints."""
import sys
import logging
from typing import Optional
from jsonrpcserver import method, dispatch, result

# Capabilities advertised during the JSON-RPC ``initialize`` handshake.
# ``tools`` is currently the only capability required by the Claude agent.
CAPABILITIES = {"tools": {}}

from openapi_server import app
from openapi_server.routes.odata import (
    services as _services,
    metadata as _metadata,
    get_entity as _get_entity,
    list_entities as _list_entities,
    invoke as _invoke,
    call_function as _call_function,
)


@method
def initialize() -> result.Result:
    """Handle the JSON-RPC initialize request."""
    return result.Success(
        {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": app.title, "version": app.version},
            "capabilities": CAPABILITIES,
        }
    )


@method
def services() -> result.Result:
    return result.Success(_services())


@method
def metadata(service: str) -> result.Result:
    return result.Success(_metadata(service))


@method
def get_entity(service: str, entity: str, keys: str, expand: Optional[str] = None) -> result.Result:
    return result.Success(_get_entity(service, entity, keys, expand))


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
) -> result.Result:
    return result.Success(
        _list_entities(service, entity, filter_, top, skip, orderby, expand, count)
    )


@method
def invoke(
    service: str, path: str, method: str = "GET", json: Optional[dict] = None
) -> result.Result:
    return result.Success(
        _invoke({"service": service, "path": path, "method": method, "json": json})
    )


@method
def call_function(service: str, name: str, body: dict) -> result.Result:
    return result.Success(_call_function(service, name, body))


def serve() -> None:
    """Run the JSON-RPC server reading from stdin and writing to stdout."""
    logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = dispatch(line)
        if response:
            print(response, flush=True)
