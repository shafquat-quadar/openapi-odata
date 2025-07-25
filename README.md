# MCP OData Bridge

This project exposes OData services using FastAPI and also provides a JSON-RPC interface for use with LLM agents. Services are discovered from a directory of metadata XML files or from a SQLite database at runtime.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Configuration is loaded from `config.yaml` if present and can be overridden with environment variables.

Example `config.yaml`:

```yaml
mode: http  # "http", "jsonrpc", or "both"
port: 8000  # HTTP server port
# dir: ./metadata
# db_file: shared.sqlite
# odata_user: username
# odata_pass: password
```

The `DIR` variable points at a directory containing service metadata XML files. Alternatively set `DB_FILE` to use a SQLite database. Credentials for backend requests can be provided via `ODATA_USER` and `ODATA_PASS`.

## Running

Use `main.py` with the `--mode` option or set `MODE` in the environment. The
HTTP port can be configured with the `--port` option or `PORT` environment
variable.

### HTTP Mode

Runs the FastAPI server with OpenAPI documentation.

```bash
python main.py --mode http
```

The interactive docs are available at `http://localhost:8000/docs` and the OpenAPI schema at `/openapi.json`.

### JSON-RPC Mode

Runs a JSON-RPC 2.0 server that reads requests from `stdin` and writes responses to `stdout`.

```bash
python main.py --mode jsonrpc
```

Example request/response:

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "services"}' | python main.py --mode jsonrpc
```

### Both Modes

Run the HTTP server and JSON-RPC handler in the same process.

```bash
python main.py --mode both --port 8000
```

## Test Commands

```bash
# HTTP mode
python main.py --mode http

# JSON-RPC mode example
printf '%s\n' '{"jsonrpc": "2.0", "id": 1, "method": "services"}' | python main.py --mode jsonrpc
```

# Both modes example
python main.py --mode both --port 8000
```
