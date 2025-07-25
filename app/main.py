from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import router from the new modular package
from routes import router
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="MCP OData Bridge", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/openapi.json", include_in_schema=False)
def openapi_schema():
    return get_openapi(title=app.title, version=app.version, routes=app.routes)
