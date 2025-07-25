"""Simple JSON-RPC 2.0 server exposing OData endpoints."""
import sys
import logging
from typing import Optional, Dict, List, Any
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

# Descriptions and parameter schemas for supported JSON-RPC tools
TOOLS: List[Dict[str, Dict]] = [
    {
        "name": "services",
        "description": "List available OData service names",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "metadata",
        "description": "Get the metadata XML for a given service",
        "inputSchema": {
            "type": "object",
            "properties": {"service": {"type": "string"}},
            "required": ["service"],
        },
    },
    {
        "name": "get_entity",
        "description": "Retrieve a single entity instance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "entity": {"type": "string"},
                "keys": {"type": "string"},
                "expand": {"type": "string"},
            },
            "required": ["service", "entity", "keys"],
        },
    },
    {
        "name": "list_entities",
        "description": "List entities within a set",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "entity": {"type": "string"},
                "filter_": {"type": "string"},
                "top": {"type": "integer"},
                "skip": {"type": "integer"},
                "orderby": {"type": "string"},
                "expand": {"type": "string"},
                "count": {"type": "boolean"},
            },
            "required": ["service", "entity"],
        },
    },
    {
        "name": "invoke",
        "description": "Perform an arbitrary backend OData request",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "path": {"type": "string"},
                "method": {"type": "string"},
                "json": {"type": "object"},
            },
            "required": ["service", "path"],
        },
    },
    {
        "name": "call_function",
        "description": "Invoke an OData function with a JSON body",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "name": {"type": "string"},
                "body": {"type": "object"},
            },
            "required": ["service", "name", "body"],
        },
    },
]


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


@method(name="tools/list")
def list_tools() -> result.Result:
    """Return metadata about available JSON-RPC tools."""
    return result.Success({"tools": TOOLS})


@method(name="tools/call")
def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> result.Result:
    """Execute one of the available tools using MCP format."""
    if arguments is None:
        arguments = {}

    if not name:
        return result.Error(code=400, message="Tool name required")
    if not isinstance(arguments, dict):
        return result.Error(code=400, message="arguments must be an object")

    tool_map = {
        "services": lambda: _services(),
        "metadata": lambda: _metadata(**arguments),
        "get_entity": lambda: _get_entity(
            arguments.get("service"),
            arguments.get("entity"),
            arguments.get("keys"),
            arguments.get("expand"),
        ),
        "list_entities": lambda: _list_entities(
            arguments.get("service"),
            arguments.get("entity"),
            arguments.get("filter_"),
            arguments.get("top"),
            arguments.get("skip"),
            arguments.get("orderby"),
            arguments.get("expand"),
            arguments.get("count"),
        ),
        "invoke": lambda: _invoke(arguments),
        "call_function": lambda: _call_function(
            arguments.get("service"),
            arguments.get("name"),
            arguments.get("body", {}),
        ),
    }

    func = tool_map.get(name)
    if not func:
        return result.Error(code=404, message="Unknown tool")

    res = func()
    return result.Success({"content": res, "contentType": "application/json"})


def serve() -> None:
    """Run the JSON-RPC server reading from stdin and writing to stdout."""
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    logger = logging.getLogger(__name__)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        logger.info("Request: %s", line)
        response = dispatch(line)
        if response:
            logger.info("Response: %s", response)
            print(response, flush=True)
