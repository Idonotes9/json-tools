import json
from jsonschema import validate, ValidationError


def validate_json_with_schema(data_file: str, schema_file: str) -> bool:
    """Validate JSON file using JSON Schema."""
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        print("Validation error:", e.message)
        return False
