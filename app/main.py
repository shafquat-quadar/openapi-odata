from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from routes import router
from typing import Any, Dict


def _convert_to_openapi_30(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAPI 3.1 schema pieces to a 3.0 compatible format."""

    def transform(obj: Any) -> None:
        if isinstance(obj, dict):
            if "anyOf" in obj and len(obj["anyOf"]) == 2 and obj["anyOf"][1].get("type") == "null":
                first = obj["anyOf"][0]
                obj.pop("anyOf")
                obj.update(first)
                obj["nullable"] = True
            for value in obj.values():
                transform(value)
        elif isinstance(obj, list):
            for item in obj:
                transform(item)

    schema["openapi"] = "3.0.3"
    transform(schema)
    return schema

# Force OpenAPI 3.0.x output for wider compatibility
app = FastAPI(
    title="MCP OData Bridge",
    version="1.0.0",
    openapi_url=None,  # disable default route so we can override
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/openapi.json", include_in_schema=False)
def openapi_schema():
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    return _convert_to_openapi_30(schema)
