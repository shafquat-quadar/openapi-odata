from typing import Any, Dict, List
import xmltodict


def _ensure_list(val: Any) -> List[Any]:
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [val]


def parse_metadata(xml: str) -> Dict[str, Any]:
    """Parse an OData V2 or V4 metadata document."""

    try:
        doc = xmltodict.parse(xml)
    except Exception as exc:
        raise ValueError(f"Invalid XML: {exc}")

    edm = doc.get("edmx:Edmx", doc)
    data_services = edm.get("edmx:DataServices") or edm.get("DataServices")
    schema = None
    if data_services:
        schema = _ensure_list(data_services.get("Schema"))[0]
    else:
        schema = _ensure_list(edm.get("Schema"))[0]

    ns_uri = schema.get("@xmlns", "")
    version = "V2" if "2008/09/edm" in ns_uri else "V4"
    namespace = schema.get("@Namespace")

    def parse_properties(obj: Any) -> List[Dict[str, Any]]:
        props = _ensure_list(obj)
        items: List[Dict[str, Any]] = []
        for p in props:
            items.append(
                {
                    "name": p.get("@Name"),
                    "type": p.get("@Type"),
                    "nullable": p.get("@Nullable", "true") != "false",
                    "max_length": p.get("@MaxLength"),
                    "precision": p.get("@Precision"),
                    "scale": p.get("@Scale"),
                    "label": p.get("sap:label"),
                    "semantics": p.get("sap:semantics"),
                    "creatable": p.get("sap:creatable", "true") != "false",
                    "updatable": p.get("sap:updatable", "true") != "false",
                    "sortable": p.get("sap:sortable", "true") != "false",
                    "filterable": p.get("sap:filterable", "true") != "false",
                }
            )
        return items

    complex_types = []
    for ct in _ensure_list(schema.get("ComplexType")):
        complex_types.append(
            {
                "name": ct.get("@Name"),
                "properties": parse_properties(ct.get("Property")),
            }
        )

    entity_types = []
    for et in _ensure_list(schema.get("EntityType")):
        keys = [k.get("@Name") for k in _ensure_list(et.get("Key", {}).get("PropertyRef"))]
        entity_types.append(
            {
                "name": et.get("@Name"),
                "keys": keys,
                "properties": parse_properties(et.get("Property")),
                "navigation": _ensure_list(et.get("NavigationProperty")),
            }
        )

    container = schema.get("EntityContainer", {})
    entity_sets = []
    for es in _ensure_list(container.get("EntitySet")):
        entity_sets.append(
            {
                "name": es.get("@Name"),
                "entity_type": es.get("@EntityType", "").split(".")[-1],
                "label": es.get("sap:label"),
            }
        )

    functions = []
    for fi in _ensure_list(container.get("FunctionImport")):
        params = []
        for p in _ensure_list(fi.get("Parameter")):
            params.append(
                {
                    "name": p.get("@Name"),
                    "type": p.get("@Type"),
                    "max_length": p.get("@MaxLength"),
                }
            )
        functions.append(
            {
                "name": fi.get("@Name"),
                "http_method": fi.get("@m:HttpMethod") or fi.get("@HttpMethod"),
                "parameters": params,
                "return_type": fi.get("@ReturnType"),
                "label": fi.get("sap:label"),
            }
        )

    return {
        "version": version,
        "namespace": namespace,
        "entity_sets": entity_sets,
        "entity_types": entity_types,
        "complex_types": complex_types,
        "functions": functions,
        "associations": [],
        "navigation": [],
        "annotations": {},
    }
