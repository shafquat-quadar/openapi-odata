from typing import Any, Dict, Optional, List, Type
from datetime import datetime
from pydantic import BaseModel, Field, create_model

# Mapping from EDM types to Python types
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


def _map_type(edm_type: str, complex_models: Dict[str, Type[BaseModel]]) -> Any:
    if not edm_type:
        return str
    if edm_type in TYPE_MAP:
        return TYPE_MAP[edm_type]
    # Complex type in same namespace
    ct_name = edm_type.split(".")[-1]
    return complex_models.get(ct_name, str)


def _build_model(name: str, props: List[Dict[str, Any]], complex_models: Dict[str, Type[BaseModel]]) -> Type[BaseModel]:
    fields: Dict[str, Any] = {}
    for prop in props:
        py_type = _map_type(prop.get("type"), complex_models)
        default = ...
        if prop.get("nullable", True):
            py_type = Optional[py_type]
            default = None
        fields[prop["name"]] = (py_type, Field(default, description=prop.get("label")))
    return create_model(name, **fields)


def build_models(metadata: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Create Pydantic models for all complex and entity types."""

    complex_models: Dict[str, Type[BaseModel]] = {}
    for ct in metadata.get("complex_types", []):
        complex_models[ct["name"]] = _build_model(ct["name"], ct.get("properties", []), complex_models)

    entity_models: Dict[str, Dict[str, Any]] = {}
    for et in metadata.get("entity_types", []):
        model = _build_model(et["name"], et.get("properties", []), complex_models)
        entity_models[et["name"]] = {
            "model": model,
            "keys": et.get("keys", []),
        }

    return {"entities": entity_models, "complex": complex_models}
