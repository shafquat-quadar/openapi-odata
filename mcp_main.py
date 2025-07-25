import sys
import json
import threading
import uvicorn
from app.main import app


def run_server() -> None:
    """Start the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


def mcp_loop() -> None:
    """Process JSON-RPC messages from stdin and write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            msg.get("jsonrpc") == "2.0"
            and msg.get("method") == "initialize"
        ):
            resp = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": {
                    "serverInfo": {
                        "name": "MCP OData Bridge",
                        "version": "1.0.0",
                    },
                    "capabilities": {
                        "odata": True,
                        "version": "1.0",
                    },
                },
            }
            print(json.dumps(resp), flush=True)


def main() -> None:
    """Run the server alongside the MCP loop."""
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    mcp_loop()


if __name__ == "__main__":
    main()
