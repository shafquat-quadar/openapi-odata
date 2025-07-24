from typing import Any, Dict, List
import xmltodict


def parse_metadata(xml: str) -> Dict[str, Any]:
    try:
        doc = xmltodict.parse(xml)
    except Exception as exc:
        raise ValueError(f"Invalid XML: {exc}")

    edm = doc.get("edmx:Edmx", doc)
    data_services = edm.get("edmx:DataServices") if isinstance(edm, dict) else None
    schema = None
    if data_services:
        schema = data_services.get("Schema")
    else:
        schema = edm.get("Schema") if isinstance(edm, dict) else None
    if isinstance(schema, list):
        schema = schema[0]
    result: Dict[str, Any] = {
        "entity_types": {},
        "entity_sets": {},
    }
    entity_types = schema.get("EntityType", [])
    if not isinstance(entity_types, list):
        entity_types = [entity_types]
    for et in entity_types:
        name = et.get("@Name")
        keys = et.get("Key", {}).get("PropertyRef", [])
        if not isinstance(keys, list):
            keys = [keys]
        key_names = [k.get("@Name") for k in keys if k]
        props = et.get("Property", [])
        if not isinstance(props, list):
            props = [props]
        parsed_props: List[Dict[str, Any]] = []
        for p in props:
            parsed_props.append(
                {
                    "name": p.get("@Name"),
                    "type": p.get("@Type"),
                    "nullable": p.get("@Nullable", "true") != "false",
                    "label": p.get("sap:label"),
                    "precision": p.get("@Precision"),
                    "scale": p.get("@Scale"),
                }
            )
        result["entity_types"][name] = {
            "name": name,
            "keys": key_names,
            "properties": parsed_props,
        }

    container = schema.get("EntityContainer", {})
    entity_sets = container.get("EntitySet", [])
    if not isinstance(entity_sets, list):
        entity_sets = [entity_sets]
    for es in entity_sets:
        if not es:
            continue
        et_name = es.get("@EntityType", "").split(".")[-1]
        result["entity_sets"][es.get("@Name")] = {
            "name": es.get("@Name"),
            "entity_type": et_name,
        }

    return result
