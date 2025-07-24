from typing import Any, Dict, List


def build_registry(service: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create a tool registry JSON description for a service."""

    tools: List[Dict[str, Any]] = []
    entity_type_map = {et["name"]: et for et in metadata.get("entity_types", [])}

    for es in metadata.get("entity_sets", []):
        et = entity_type_map.get(es["entity_type"], {})
        key_params = [f"{k}={{key}}" for k in et.get("keys", [])]
        key_url = ",".join(key_params)

        tools.append(
            {
                "name": f"list_{es['name'].lower()}",
                "method": "GET",
                "path": f"/{service}/{es['name']}",
                "params": {
                    "$filter": "optional string",
                    "$top": "optional int",
                    "$skip": "optional int",
                    "$orderby": "optional string",
                    "$expand": "optional string",
                    "$count": "optional bool",
                },
                "returns": f"List[{es['entity_type']}]",
            }
        )

        tools.append(
            {
                "name": f"get_{es['name'].lower()}",
                "method": "GET",
                "path": f"/{service}/{es['name']}({key_url})",
                "params": {},
                "returns": es["entity_type"],
            }
        )

    for fi in metadata.get("functions", []):
        param_spec = {p["name"]: p.get("type", "string") for p in fi.get("parameters", [])}
        tools.append(
            {
                "name": fi["name"],
                "method": "POST",
                "path": f"/invoke/{service}/{fi['name']}",
                "params": param_spec,
                "returns": fi.get("return_type", "object"),
            }
        )

    return {"service": service, "tools": tools}
