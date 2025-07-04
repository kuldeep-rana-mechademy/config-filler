from rich import print as pp
import json
import os
from typing import Any, Dict, List, Optional


def extract_config_from_schema(schema):
    """
    Extract a base configuration template from a JSON schema.

    Args:
        schema (dict): JSON schema dictionary

    Returns:
        dict: Base configuration template with default values
    """

    def resolve_ref(ref, base_schema):
        """Resolve a JSON schema reference"""
        if not ref.startswith("#/"):
            raise ValueError(f"External references not supported: {ref}")

        path = ref[2:].split("/")
        current = base_schema
        for part in path:
            if part in current:
                current = current[part]
            else:
                raise ValueError(f"Invalid reference: {ref}")
        return current

    def process_schema_object(obj_schema):
        base_obj = {}

        # Handle $ref at the object level
        if "$ref" in obj_schema:
            referenced_schema = resolve_ref(obj_schema["$ref"], schema)
            return process_schema_object(referenced_schema)

        # Process properties if they exist
        properties = obj_schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            # Handle $ref in property
            if "$ref" in prop_schema:
                referenced_schema = resolve_ref(prop_schema["$ref"], schema)
                base_obj[prop_name] = process_schema_object(referenced_schema)
                continue

            # Handle different types of properties
            prop_type = prop_schema.get("type")

            if prop_type == "object":
                # Recursively process nested objects
                base_obj[prop_name] = process_schema_object(prop_schema)

            elif prop_type == "array":
                # Initialize arrays as empty lists
                base_obj[prop_name] = []

            elif prop_type in ["string", "number", "integer", "boolean", None]:
                # For simple types, use default if available, otherwise None
                if "default" in prop_schema:
                    base_obj[prop_name] = prop_schema["default"]
                elif "enum" in prop_schema and prop_schema["enum"]:
                    # For enums without defaults, you might want to use the first value
                    # base_obj[prop_name] = prop_schema['enum'][0]
                    base_obj[prop_name] = None
                else:
                    base_obj[prop_name] = None
            else:
                # Unknown type
                base_obj[prop_name] = None

        return base_obj

    # Process the root schema
    if schema.get("type") == "object":
        return process_schema_object(schema)
    else:
        raise ValueError("Root schema must be of type 'object'")


def save_config_to_file(
    final_config: Any, filename: str, directory: str = "Data/generated_config"
) -> None:
    os.makedirs(directory, exist_ok=True)
    config_filename = os.path.join(directory, f"config_{filename}.json")
    try:
        if isinstance(final_config, str):
            try:
                final_config = json.loads(final_config)
            except json.JSONDecodeError:
                with open(config_filename, "w") as f:
                    f.write(final_config)
                pp(f"[yellow]Saved raw text (not JSON) to {config_filename}[/yellow]")
                return
        with open(config_filename, "w") as f:
            json.dump(final_config, f, indent=2)
        pp(f"[green]Saved configuration to {config_filename}[/green]")
    except Exception as e:
        pp(f"[red]Error saving configuration to {config_filename}: {e}[/red]")
