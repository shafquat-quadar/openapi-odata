# MCP OData Bridge

This project exposes OData services using FastAPI and also provides a JSON-RPC interface for use with LLM agents. Services are discovered from a directory of metadata XML files or from a SQLite database at runtime.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Configuration is loaded from `config.yaml`. Environment variables are ignored.

Example `config.yaml`:

```yaml
mode: http  # "http", "jsonrpc", or "both"
port: 8000  # HTTP server port
# dir: ./metadata
# db_file: shared.sqlite
# base_url: https://sapes5.sapdevcenter.com/sap/opu/odata/sap
# odata_user: username
# odata_pass: password
```

Set `dir` to point at a directory containing service metadata XML files. Alternatively set `db_file` to use a SQLite database. Credentials for backend requests can be provided via `odata_user` and `odata_pass`. `base_url` sets the default OData endpoint used for backend requests when a service metadata file does not specify one.

## Running

Use `main.py` with the `--mode` option to start the server. The HTTP port can
be changed with the `--port` option.

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

Logs of all requests and responses are written to `jsonrpc_server/jsonrpc.log`.

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

## CopilotStudio Client Environment

The optional `CopilotStudioClient` reads configuration values from a `.env` file.
Create a file named `.env` in the project root and provide the following variables:

```
environmentId="<YOUR_ENVIRONMENT_ID>"
agentIdentifier="<YOUR_AGENT_IDENTIFIER>"
tenantId="<YOUR_TENANT_ID>"
appClientId="<YOUR_APP_CLIENT_ID>"
```

These values are used when initializing `CopilotStudioClient`.
