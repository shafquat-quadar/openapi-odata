from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec
from app.main import app

client = TestClient(app)
resp = client.get("/openapi.json")
resp.raise_for_status()
validate_spec(resp.json())
print("OpenAPI schema is valid")
