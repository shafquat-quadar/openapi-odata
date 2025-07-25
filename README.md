# openapi-odata

This project implements a small MCP style bridge that exposes OData services via FastAPI. Service definitions can come from a SQLite database or from a directory of metadata XML files. The metadata is parsed at runtime to create Pydantic models, FastAPI routes and a tool registry consumable by LLM agents.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Choose how services are loaded:
   - **SQLite** (default): the SQLite file used is configured with the `DB_FILE`
     environment variable (`shared.sqlite` by default). The table
     `odata_services` must contain `service_name`, `base_url` and
     `metadata_raw` columns.
   - **Directory**: set `DIR=./path/to/xmls`. Each `*.xml` file in the directory
     is treated as a service. Optional `BASE_URL_<SERVICE>` variables can provide
     per-service backend URLs.
   You can fetch the XML from a running service using the `fetch_metadata.py`
   helper.

3. Provide credentials in an `.env` file or environment variables:
   - `ODATA_USER` and `ODATA_PASS` – credentials used for Basic Auth when the
     bridge calls the backend service.

   **Note:** the server refuses to start if `ODATA_USER` or `ODATA_PASS` are not
   defined.

The helper script `fetch_metadata.py` honours the `ODATA_BASE_URL`, `ODATA_USER`
and `ODATA_PASS` variables when downloading metadata from an existing OData
service.

4. Run the server:
   ```bash
   python path/to/openapi-odata
   ```
   The package can still be started manually with Uvicorn using `uvicorn app.main:app` if preferred.

The `/openapi.json` endpoint exposes the combined OpenAPI specification while `/tools/{service}` returns tool metadata for a single service.
