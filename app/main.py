from fastapi import FastAPI
from .routes import router
from .tool_registry import generate_spec

app = FastAPI(title="MCP OData Bridge", version="1.0.0")
app.include_router(router)


@app.get("/openapi.json", include_in_schema=False)
def openapi_schema():
    return generate_spec(app)
