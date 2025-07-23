# openapi-odata

This project exposes an OData service as a FastAPI application. The server reads
the OData `$metadata` document, dynamically creates Pydantic models and
endpoints for each entity set, and exposes them via a generated OpenAPI 3.1
schema.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Provide environment variables:
   - `ODATA_SERVICE_URL` – base URL of the OData service.
   - `ODATA_USERNAME` and `ODATA_PASSWORD` – credentials for basic auth.
   - `ODATA_METADATA_FILE` – optional path to a local `$metadata` XML file.

3. Run the server:
   ```bash
   uvicorn app.main:app
   ```

The generated OpenAPI document is available at `/openapi.json`.
