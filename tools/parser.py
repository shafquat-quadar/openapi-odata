"""Parse OData V2 metadata."""

from __future__ import annotations

from typing import Any, Dict, List
import xmltodict


def _ensure_list(val: Any) -> List[Any]:
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [val]


def parse_metadata(xml: str) -> Dict[str, Any]:
    doc = xmltodict.parse(xml)
    edm = doc.get("edmx:Edmx", doc)
    ds = edm.get("edmx:DataServices") or edm.get("DataServices")
    schema = _ensure_list(ds.get("Schema"))[0]

    res: Dict[str, Any] = {"entity_types": [], "entity_sets": [], "functions": [], "associations": [], "navigation": []}
    res["namespace"] = schema.get("@Namespace")

    for et in _ensure_list(schema.get("EntityType")):
        keys = [k.get("@Name") for k in _ensure_list(et.get("Key", {}).get("PropertyRef"))]
        props = []
        for p in _ensure_list(et.get("Property")):
            props.append({
                "name": p.get("@Name"),
                "type": p.get("@Type"),
                "nullable": p.get("@Nullable", "true") != "false",
                "label": p.get("sap:label"),
            })
        nav = []
        for n in _ensure_list(et.get("NavigationProperty")):
            nav.append({"name": n.get("@Name"), "relationship": n.get("@Relationship"), "to_role": n.get("@ToRole"), "from_role": n.get("@FromRole")})
        res["entity_types"].append({"name": et.get("@Name"), "keys": keys, "properties": props, "navigation": nav})

    container = schema.get("EntityContainer", {})
    for es in _ensure_list(container.get("EntitySet")):
        res["entity_sets"].append({"name": es.get("@Name"), "entity_type": es.get("@EntityType", "").split(".")[-1]})

    for fi in _ensure_list(container.get("FunctionImport")):
        params = []
        for p in _ensure_list(fi.get("Parameter")):
            params.append({"name": p.get("@Name"), "type": p.get("@Type")})
        res["functions"].append({"name": fi.get("@Name"), "http_method": fi.get("@m:HttpMethod") or fi.get("@HttpMethod", "GET"), "parameters": params})

    for assoc in _ensure_list(schema.get("Association")):
        res["associations"].append({"name": assoc.get("@Name")})

    for aset in _ensure_list(container.get("AssociationSet")):
        res["navigation"].append({"name": aset.get("@Name")})

    return res
