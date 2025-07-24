# openapi-odata

This project implements a small MCP style bridge that exposes OData services via FastAPI. Metadata is stored in a SQLite database and parsed at runtime to create Pydantic models and routes.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `shared.sqlite` with a `services` table containing columns `id`, `name`, `metadata_xml`, `active`, `description`, and `base_url`.

3. Provide credentials in an `.env` file or environment variables:
   - `ODATA_USERNAME` and `ODATA_PASSWORD` – Basic Auth credentials.

4. Run the server:
   ```bash
   uvicorn app.main:app
   ```

The `/openapi.json` endpoint exposes the combined OpenAPI specification while `/tools/{service}` returns tool metadata for a single service.
