"""Entry point for running in HTTP or JSON-RPC mode."""
import argparse
import threading
import uvicorn

from config import settings
from openapi_server import app
from jsonrpc_server import serve as serve_jsonrpc


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP OData Bridge")
    parser.add_argument(
        "--mode",
        choices=["http", "jsonrpc", "both"],
        default=settings.mode,
        help="Server mode",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help="HTTP server port",
    )
    args = parser.parse_args()
    mode = args.mode
    port = args.port
    if mode == "jsonrpc":
        serve_jsonrpc()
    elif mode == "http":
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:  # both
        t = threading.Thread(target=serve_jsonrpc, daemon=True)
        t.start()
        uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
