# openapi-odata

This project implements a small MCP style bridge that exposes OData services via
FastAPI. Metadata is loaded from an XML file placed in the project directory and
parsed at runtime to create Pydantic models and routes.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place your OData metadata in an XML file (default: `sample_metadata.xml`).
   You can override the location with the `METADATA_XML_FILE` environment
   variable. The target backend URL can be customised via `ODATA_BASE_URL`.

3. Provide credentials in an `.env` file or environment variables:
   - `ODATA_USERNAME` and `ODATA_PASSWORD` – Basic Auth credentials.

4. Run the server:
   ```bash
   uvicorn app.main:app
   ```

The `/openapi.json` endpoint exposes the combined OpenAPI specification while `/tools/{service}` returns tool metadata for a single service.
