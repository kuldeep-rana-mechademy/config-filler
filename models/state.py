import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator


class EquipmentState(BaseModel):
    """
    Model representing data extracted from the PDF including markdown, schema, and stage-throw information.

    Fields:
    - markdown_text: Raw markdown extracted from the PDF file.
    - extracted_schema: Extracted JSON schema from the markdown.
    - throw_stage_comb: List of stage-to-throw combinations extracted from the markdown.
    - required_stage_throw: Currently selected or required stage-to-throw combination.
    - dict_from_markdown: Dictionary parsed from the extracted markdown text.
    - base_config: Base configuration JSON string.
    - calculation_results: Dictionary of results computed from the configuration.
    - final_config: Final configuration JSON string after processing and calculations.
    """

    markdown_text: Optional[str] = Field(
        None, description="Markdown extracted from PDF"
    )
    extracted_schema: Optional[Dict[str, Any]] = Field(
        None, description="Extracted JSON schema"
    )
    throw_stage_comb: Optional[List[str]] = Field(
        default_factory=list, description="List of throw-stage combinations"
    )
    required_stage_throw: Optional[str] = Field(
        None, description="Current throw-stage combination"
    )
    dict_from_markdown: Optional[Dict[str, Any]] = Field(
        None, description="Dictionary created from markdown"
    )
    base_config: Optional[str] = Field(
        None, description="Base configuration JSON string"
    )
    calculation_results: Dict[str, Any] = Field(
        default_factory=dict, description="Compressor calculation results"
    )
    final_config: Optional[str] = Field(
        None, description="Final configuration JSON string"
    )

    @field_validator("markdown_text")
    @classmethod
    def validate_markdown_text(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Markdown text cannot be empty if provided")
        return value

    @field_validator("throw_stage_comb")
    @classmethod
    def validate_throw_stage_comb(
        cls, value: Optional[List[str]]
    ) -> Optional[List[str]]:
        if value is not None:
            for item in value:
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(
                        "All throw stage combinations must be non-empty strings"
                    )
        return value

    @field_validator("extracted_schema", "dict_from_markdown")
    @classmethod
    def validate_dict(cls, value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if value is not None and not isinstance(value, dict):
            raise ValueError("Value must be a dictionary")
        return value

    @field_validator("base_config", "final_config")
    @classmethod
    def validate_json(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            try:
                json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        return value
