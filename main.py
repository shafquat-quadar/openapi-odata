"""Entry point for running in HTTP or JSON-RPC mode."""
import argparse
import uvicorn

from config import settings
from openapi_server import app
from jsonrpc_server import serve as serve_jsonrpc


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP OData Bridge")
    parser.add_argument(
        "--mode",
        choices=["http", "jsonrpc"],
        default=settings.mode,
        help="Server mode",
    )
    args = parser.parse_args()
    mode = args.mode
    if mode == "jsonrpc":
        serve_jsonrpc()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
