from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class OutputDataValidator(BaseModel):
    data: Dict[str, Any] = Field(..., description="Dictionary with key-value pairs")


class InputDataValidator(BaseModel):
    """
    Model representing the input data required for processing equipment configuration.

    Fields:
    - equipment_name: Name of the equipment (e.g., "reciprocating compressor", "induction motor").
    - pdf_path: Path to the input PDF datasheet.
    - schema_path: Path to the JSON configuration schema.
    - constant_params: Dictionary of constant parameters like valve quantities and others.
    """

    equipment_name: str = Field(..., min_length=1, description="Name of the equipment")
    pdf_path: str = Field(..., description="Path to input PDF datasheet")
    # schema_path: str = Field(..., description="Path to JSON config schema")
    constant_params: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Constant parameters (e.g., valve quantities)"
    )

    @field_validator("pdf_path")
    @classmethod
    def validate_pdf_path(cls, value: str) -> str:
        path = Path(value)
        if not path.exists() or not path.is_file() or path.suffix.lower() != ".pdf":
            raise ValueError(f"Invalid PDF path: {value}")
        return str(path.resolve())

    # @field_validator("schema_path")
    # @classmethod
    # def validate_schema_path(cls, value: str) -> str:
    #     path = Path(value)
    #     if not path.exists() or not path.is_file() or path.suffix.lower() != ".json":
    #         raise ValueError(f"Invalid schema path: {value}")
    #     try:
    #         with open(path, "r", encoding="utf-8") as f:
    #             json.load(f)
    #     except json.JSONDecodeError as e:
    #         raise ValueError(f"Invalid JSON file: {value}. Error: {e}")
    #     return str(path.resolve())

    @field_validator("equipment_name")
    @classmethod
    def validate_equipment_name(cls, value: str) -> str:
        valid_types = [
            "reciprocating compressor",
            "induction motor",
            "screw compressor",
            "centrifugal compressor",
        ]
        if value.lower() not in [t.lower() for t in valid_types]:
            raise ValueError(
                f"Invalid equipment name: {value}. Must be one of {valid_types}"
            )
        return value

    @field_validator("constant_params")
    @classmethod
    def validate_constant_params(
        cls, value: Dict[str, Dict[str, Any]], info: ValidationInfo
    ) -> Dict[str, Dict[str, Any]]:
        equipment_name = info.data.get("equipment_name", "").lower()
        if equipment_name == "reciprocating compressor":
            required_keys = [
                "he_suction_valve_quantity",
                "he_discharge_valve_quantity",
                "ce_suction_valve_quantity",
                "ce_discharge_valve_quantity",
            ]
            for key in required_keys:
                if key not in value:
                    raise ValueError(f"Missing required constant parameter: {key}")
                if not isinstance(value[key], dict) or "value" not in value[key]:
                    raise ValueError(f"Invalid format for constant parameter: {key}")
        return value
