def postprocess_facets(result, generator, request, public):
    work_type_facet_component = {
        "type": "object",
        "required": ["id", "key", "count"],
        "properties": {
            "id": {"type": "integer"},
            "key": {"type": "string"},
            "count": {"type": "integer"},
            "children": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/WorkTypeFacet"},
            },
        },
    }
    result["components"]["schemas"]["WorkTypeFacet"] = work_type_facet_component
    return result
