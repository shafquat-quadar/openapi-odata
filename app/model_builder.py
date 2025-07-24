from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, create_model, Field

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


def build_models(metadata: Dict[str, Any]) -> Dict[str, BaseModel]:
    models: Dict[str, BaseModel] = {}
    for es_name, es in metadata["entity_sets"].items():
        et = metadata["entity_types"].get(es["entity_type"]) or {}
        fields: Dict[str, Any] = {}
        for prop in et.get("properties", []):
            py_type = TYPE_MAP.get(prop["type"], str)
            default = ...
            if prop.get("nullable", True):
                py_type = Optional[py_type]
                default = None
            field_desc = prop.get("label")
            fields[prop["name"]] = (py_type, Field(default, description=field_desc))
        model = create_model(es["entity_type"], **fields)
        models[es_name] = model
    return models
