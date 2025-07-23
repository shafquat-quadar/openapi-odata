import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, create_model
import pyodata

ODATA_SERVICE_URL = os.getenv("ODATA_SERVICE_URL", "http://example.com/odata/")
ODATA_USERNAME = os.getenv("ODATA_USERNAME", "user")
ODATA_PASSWORD = os.getenv("ODATA_PASSWORD", "password")

session = requests.Session()
session.auth = (ODATA_USERNAME, ODATA_PASSWORD)

# Fetch metadata. In restricted environments this may not work if the URL is not reachable
# so we allow loading metadata from a local file via ODATA_METADATA_FILE.
metadata_file = os.getenv("ODATA_METADATA_FILE")
if metadata_file:
    with open(metadata_file, "rb") as f:
        metadata_bytes = f.read()
else:
    resp = session.get(ODATA_SERVICE_URL.rstrip("/") + "/$metadata")
    resp.raise_for_status()
    metadata_bytes = resp.content

client = pyodata.Client(ODATA_SERVICE_URL, session, metadata=metadata_bytes)

app = FastAPI(openapi_version="3.1.0")

# Mapping from OData EDM primitive types to Python types
TYPE_MAP = {
    "Edm.String": str,
    "Edm.Int32": int,
    "Edm.Int16": int,
    "Edm.Int64": int,
    "Edm.Double": float,
    "Edm.Single": float,
    "Edm.Decimal": float,
    "Edm.Boolean": bool,
    "Edm.DateTime": datetime,
}

models: Dict[str, BaseModel] = {}

for entity_set in client.schema.entity_sets:
    etype = entity_set.entity_type
    fields: Dict[str, Tuple[Any, Any]] = {}
    for prop in etype.proprties():
        py_type = TYPE_MAP.get(prop.typ.name, Any)
        if prop.nullable:
            py_type = Optional[py_type]
        default = None if prop.nullable else ...
        fields[prop.name] = (py_type, default)
    model = create_model(etype.name, **fields)
    models[entity_set.name] = model

    def make_list_entities(name: str, mdl: BaseModel):
        @app.get(f"/{name}", response_model=List[mdl], name=f"get_{name}")
        def list_entities() -> List[mdl]:
            url = ODATA_SERVICE_URL.rstrip("/") + f"/{name}"
            resp = session.get(url)
            if resp.status_code != 200:
                raise HTTPException(resp.status_code, resp.text)
            return resp.json().get("value", [])
        return list_entities

    def make_create_entity(name: str, mdl: BaseModel):
        @app.post(f"/{name}", response_model=mdl, name=f"create_{name}")
        def create_entity(item: mdl) -> mdl:
            url = ODATA_SERVICE_URL.rstrip("/") + f"/{name}"
            resp = session.post(url, json=item.model_dump(exclude_none=True))
            if resp.status_code not in (200, 201):
                raise HTTPException(resp.status_code, resp.text)
            return resp.json()
        return create_entity

    def make_get_entity(name: str, mdl: BaseModel):
        @app.get(f"/{name}/{{key}}", response_model=mdl, name=f"get_{name}_by_key")
        def get_entity(key: str) -> mdl:
            url = ODATA_SERVICE_URL.rstrip("/") + f"/{name}({key})"
            resp = session.get(url)
            if resp.status_code != 200:
                raise HTTPException(resp.status_code, resp.text)
            return resp.json()
        return get_entity

    def make_update_entity(name: str, mdl: BaseModel):
        @app.patch(f"/{name}/{{key}}", response_model=mdl, name=f"update_{name}")
        def update_entity(key: str, item: mdl) -> mdl:
            url = ODATA_SERVICE_URL.rstrip("/") + f"/{name}({key})"
            resp = session.patch(url, json=item.model_dump(exclude_none=True))
            if resp.status_code != 204:
                raise HTTPException(resp.status_code, resp.text)
            resp = session.get(url)
            resp.raise_for_status()
            return resp.json()
        return update_entity

    def make_delete_entity(name: str):
        @app.delete(f"/{name}/{{key}}", name=f"delete_{name}")
        def delete_entity(key: str):
            url = ODATA_SERVICE_URL.rstrip("/") + f"/{name}({key})"
            resp = session.delete(url)
            if resp.status_code not in (200, 204):
                raise HTTPException(resp.status_code, resp.text)
            return {"deleted": True}
        return delete_entity

    make_list_entities(entity_set.name, model)
    make_create_entity(entity_set.name, model)
    make_get_entity(entity_set.name, model)
    make_update_entity(entity_set.name, model)
    make_delete_entity(entity_set.name)

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    schema = get_openapi(
        title="OData Converted Service",
        version="1.0.0",
        routes=app.routes,
    )
    return schema

