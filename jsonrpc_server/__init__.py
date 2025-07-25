"""Simple JSON-RPC 2.0 server exposing OData endpoints."""
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from jsonrpcserver import method, dispatch, result
from starlette.responses import Response
import json

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


def _as_raw(value: Any) -> Any:
    """Return the content from a FastAPI Response or passthrough."""
    if isinstance(value, Response):
        text = value.body.decode()
        try:
            return json.loads(text)
        except Exception:
            return text
    return value

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
def initialize(
    protocolVersion: Optional[str] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    clientInfo: Optional[Dict[str, Any]] = None,
    **_kwargs: Any,
) -> result.Result:
    """Handle the JSON-RPC initialize request.

    Parameters are accepted for compatibility with clients that send them
    during the initialize handshake. They are not currently used, but the
    presence of these optional parameters prevents ``InvalidParams`` errors
    from the dispatcher.
    """

    # Ignore the requested protocol version and always respond with the
    # standard version supported by this server.
    _ = (protocolVersion, capabilities, clientInfo, _kwargs)

    print(
        f"DEBUG: initialize called with protocolVersion={protocolVersion}, capabilities={capabilities}, clientInfo={clientInfo}",
        file=sys.stderr,
    )
    try:
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": app.title, "version": app.version},
            "capabilities": CAPABILITIES,
        }
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method
def services() -> result.Result:
    print("DEBUG: services called", file=sys.stderr)
    try:
        res = _as_raw(_services())
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method
def metadata(service: str) -> result.Result:
    print(f"DEBUG: metadata called with service={service}", file=sys.stderr)
    try:
        res = _as_raw(_metadata(service))
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method
def get_entity(service: str, entity: str, keys: str, expand: Optional[str] = None) -> result.Result:
    print(
        f"DEBUG: get_entity called with service={service}, entity={entity}, keys={keys}, expand={expand}",
        file=sys.stderr,
    )
    try:
        res = _as_raw(_get_entity(service, entity, keys, expand))
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


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
    print(
        "DEBUG: list_entities called with "
        f"service={service}, entity={entity}, filter_={filter_}, top={top}, "
        f"skip={skip}, orderby={orderby}, expand={expand}, count={count}",
        file=sys.stderr,
    )
    try:
        res = _list_entities(
            service, entity, filter_, top, skip, orderby, expand, count
        )
        res = _as_raw(res)
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method
def invoke(
    service: str, path: str, method: str = "GET", json: Optional[dict] = None
) -> result.Result:
    print(
        f"DEBUG: invoke called with service={service}, path={path}, method={method}, json={json}",
        file=sys.stderr,
    )
    try:
        res = _invoke({"service": service, "path": path, "method": method, "json": json})
        res = _as_raw(res)
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method
def call_function(service: str, name: str, body: dict) -> result.Result:
    print(
        f"DEBUG: call_function called with service={service}, name={name}, body={body}",
        file=sys.stderr,
    )
    try:
        res = _call_function(service, name, body)
        res = _as_raw(res)
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


@method(name="tools/list")
def list_tools() -> result.Result:
    """Return metadata about available JSON-RPC tools."""
    print("DEBUG: list_tools called", file=sys.stderr)
    try:
        res = {"tools": TOOLS}
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success(res)
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


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
        "services": lambda: _as_raw(_services()),
        "metadata": lambda: _as_raw(_metadata(**arguments)),
        "get_entity": lambda: _as_raw(
            _get_entity(
                arguments.get("service"),
                arguments.get("entity"),
                arguments.get("keys"),
                arguments.get("expand"),
            )
        ),
        "list_entities": lambda: _as_raw(
            _list_entities(
                arguments.get("service"),
                arguments.get("entity"),
                arguments.get("filter_"),
                arguments.get("top"),
                arguments.get("skip"),
                arguments.get("orderby"),
                arguments.get("expand"),
                arguments.get("count"),
            )
        ),
        "invoke": lambda: _as_raw(_invoke(arguments)),
        "call_function": lambda: _as_raw(
            _call_function(
                arguments.get("service"),
                arguments.get("name"),
                arguments.get("body", {}),
            )
        ),
    }

    func = tool_map.get(name)
    if not func:
        return result.Error(code=404, message="Unknown tool")

    print(f"DEBUG: About to call {name} with {arguments}", file=sys.stderr)
    try:
        res = func()
        print(f"DEBUG: Got result: {res}", file=sys.stderr)
        return result.Success({"content": res, "contentType": "application/json"})
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}", file=sys.stderr)
        return result.Error(code=500, message=str(e))


def serve() -> None:
    """Run the JSON-RPC server reading from stdin and writing to stdout."""
    log_file = Path(__file__).with_name("jsonrpc.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file, mode="a"),
        ],
    )
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
