# openapi-odata

This project implements a small MCP style bridge that exposes OData services via FastAPI. Service definitions can come from a SQLite database or from a directory of metadata XML files. The metadata is parsed at runtime to create Pydantic models, FastAPI routes and a tool registry consumable by LLM agents.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Choose how services are loaded:
   - **SQLite** (default): Insert your service configuration into `shared.sqlite`. The table `services` must contain `name`, `description`, `active`, `metadata_xml` and `base_url` columns.
   - **Directory**: Set `METADATA_SOURCE=dir` and `METADATA_DIR=./path/to/xmls`. Each `*.xml` file is treated as a service named after the filename. Optional `BASE_URL_SERVICE` environment variables can provide per-service backend URLs.
   You can fetch the XML from a running service using the `fetch_metadata.py` helper.

3. Provide credentials in an `.env` file or environment variables:
   - `USERNAME` and `PASSWORD` – Basic Auth credentials for the backend
   - `BASE_URL` (optional) – default backend base URL

4. Run the server:
   ```bash
   uvicorn app.main:app
   ```

The `/openapi.json` endpoint exposes the combined OpenAPI specification while `/tools/{service}` returns tool metadata for a single service.
