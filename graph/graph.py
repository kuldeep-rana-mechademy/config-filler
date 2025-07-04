from models.model import InputDataValidator, OutputDataValidator
from models.state import EquipmentState
from prompts.prompts import (
    recip_comp_dict_prompt,
    screw_comp_dict_prompt,
    centri_comp_dict_prompt,
    induction_motor_dict_prompt,
    data_mapping_prompt,
    recip_stage_throw_extraction_prompt,
    recip_tool_call_prompt,
    final_mapping_prompt,
)
from tools.recip_tools import (
    head_end_area,
    crank_end_area,
    head_end_displacement,
    crank_end_displacement,
    swept_volume,
    head_end_clearances,
    crank_end_clearances,
    mean_piston_speed,
    he_suction_valve_diameter,
    he_discharge_valve_diameter,
    ce_suction_valve_diameter,
    ce_discharge_valve_diameter,
)
from langchain_core.output_parsers import (
    StrOutputParser,
    PydanticOutputParser,
    JsonOutputParser,
)
import logging
from utils.prompt_management import LangfusePromptManager
from functools import wraps
from langgraph.graph import StateGraph, END, START
import os
import pymupdf4llm
from utils.utils import extract_config_from_schema, save_config_to_file
from utils.equipment_configs import equipment_configs
import json
from langfuse.callback import CallbackHandler
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from rich import print as pp
from IPython.display import Image
import io


def ensure_llm(func):
    @wraps(func)
    def wrapper(self, state: EquipmentState, llm=None, *args, **kwargs):
        if llm is None:
            llm = self.llm
        return func(self, state, llm, *args, **kwargs)

    return wrapper


class EquipmentGraph:
    def __init__(self, input_data: InputDataValidator, llm, logging=False):
        """
        Initialize EquipmentGraph with state, validator, and LLM.

        Args:
            state (EquipmentState): Initial state for the workflow.
            validator (InputDataValidator): Validated input data for equipment processing.
            llm: Language model instance for processing prompts.
            logging (bool): Enable Langfuse logging if True.

        Raises:
            TypeError: If validator is not an instance of InputDataValidator.
        """

        self.llm = llm
        self.state = EquipmentState()
        self.validator = input_data
        if logging:
            self.langfuse_handler = [
                CallbackHandler(
                    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
                    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
                    host=os.environ.get("LANGFUSE_ENDPOINT"),
                )
            ]
        else:
            self.langfuse_handler = []
        self.logging = logging
        self.prompt_manager = LangfusePromptManager(logging)

    @ensure_llm
    def extract_pdf_node(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """Extract markdown from PDF and update state."""
        try:
            markdown_text = str(pymupdf4llm.to_markdown(self.validator.pdf_path))
            if not isinstance(markdown_text, str) or not markdown_text.strip():
                raise ValueError("Failed to extract valid markdown from PDF")
            state.markdown_text = markdown_text
            return state
        except Exception as e:
            raise RuntimeError(f"Error extracting PDF to markdown: {e}")

    @ensure_llm
    def extract_schema_node(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """Extract JSON schema from file and update state."""
        try:
            schema = equipment_configs.get(self.validator.equipment_name.lower(), {})
            if not schema:
                raise ValueError("No schema found for the equipment type")
            extracted_schema = extract_config_from_schema(schema)
            if extracted_schema is None:
                raise ValueError("Failed to extract schema")
            state.extracted_schema = extracted_schema
            return state
        except Exception as e:
            raise RuntimeError(f"Error extracting config schema: {e}")

    @ensure_llm
    def create_dict_node(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """
        Extract a structured configuration dictionary from markdown using LLM and update state.

        Args:
            state: EquipmentState object containing markdown text.
            llm: Optional language model instance; defaults to self.llm.

        Returns:
            EquipmentState: Updated state with dict_from_markdown populated.

        Raises:
            ValueError: If markdown_text is missing.
            RuntimeError: If LLM processing or validation fails.
        """
        if not state.markdown_text:
            raise ValueError("Markdown text is missing")

        try:
            equipment_name = self.validator.equipment_name.lower()
            if equipment_name == "reciprocating compressor":
                prompt = self.prompt_manager.get_langchain_prompt(
                    recip_comp_dict_prompt
                )
            elif equipment_name == "induction motor":
                prompt = self.prompt_manager.get_langchain_prompt(
                    induction_motor_dict_prompt
                )
            elif equipment_name == "screw compressor":
                prompt = self.prompt_manager.get_langchain_prompt(
                    screw_comp_dict_prompt
                )
            elif equipment_name == "centrifugal compressor":
                prompt = self.prompt_manager.get_langchain_prompt(
                    centri_comp_dict_prompt
                )
            else:
                raise ValueError(f"No prompt defined for equipment: {equipment_name}")

            prompt_str = prompt.format(
                markdown_text=state.markdown_text,
                combination=state.throw_stage_comb or "not available",
                require_stage_throw=state.required_stage_throw or "not available",
                format_instructions=PydanticOutputParser(
                    pydantic_object=OutputDataValidator
                ).get_format_instructions(),
            )
            chain = llm | StrOutputParser()
            response = chain.invoke(prompt_str)
            validated_response = OutputDataValidator.model_validate_json(response)
            final_dict = validated_response.data
            final_dict.update(self.validator.constant_params)
            state.dict_from_markdown = final_dict
            return state
        except Exception as e:
            raise RuntimeError(f"Error creating datasheet dictionary: {e}")

    @ensure_llm
    def create_base_config_node(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """
        Generate base configuration using LLM and save to file.

        Args:
            state: EquipmentState object containing extracted data.
            llm: Optional language model instance; defaults to self.llm.

        Returns:
            EquipmentState: Updated state with base_config populated.

        Raises:
            RuntimeError: If LLM processing or validation fails.
        """
        try:
            prompt = self.prompt_manager.get_langchain_prompt(data_mapping_prompt)
            prompt_str = prompt.format(
                equipment_name=self.validator.equipment_name,
                data_sheet_dict=state.dict_from_markdown,
                config_schema_dict=state.extracted_schema,
                format_instructions=PydanticOutputParser(
                    pydantic_object=OutputDataValidator
                ).get_format_instructions(),
            )
            chain = llm | StrOutputParser()
            response = chain.invoke(prompt_str)
            validated_response = OutputDataValidator.model_validate_json(response)
            state.base_config = response
            equipment_name = self.validator.equipment_name.lower()
            file_name = {
                "reciprocating compressor": "Reciprocating_Compressor",
                "induction motor": "Induction_Motor",
                "screw compressor": "Screw_Compressor",
                "centrifugal compressor": "Centrifugal_Compressor",
            }.get(equipment_name, equipment_name.replace(" ", "_"))
            if equipment_name != "reciprocating compressor":
                save_config_to_file(validated_response.data, file_name)
            return state
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise RuntimeError(f"Error creating base configuration: {e}")

    @ensure_llm
    def recip_comp_node(self, state: EquipmentState, llm: str = None) -> EquipmentState:
        """
        Extract throw-stage combinations for reciprocating compressors using LLM and update state.

        Args:
            state: EquipmentState object containing markdown text.
            llm: Optional language model instance; defaults to self.llm.

        Returns:
            EquipmentState: Updated state with throw-stage combinations and required stage-throw.

        Raises:
            ValueError: If markdown_text is missing.
            RuntimeError: For errors during LLM processing.
        """
        if not state.markdown_text:
            raise ValueError("Markdown text is missing")

        try:
            prompt = self.prompt_manager.get_langchain_prompt(
                recip_stage_throw_extraction_prompt
            )
            prompt_str = prompt.format(
                markdown_text=state.markdown_text,
            )
            chain = llm | StrOutputParser()
            throw_stage_comb = chain.invoke(prompt_str)
            combinations = (
                [combo.strip() for combo in throw_stage_comb.split(",")]
                if isinstance(throw_stage_comb, str)
                else throw_stage_comb
            )
            state.throw_stage_comb = combinations
            state.required_stage_throw = combinations[0] if combinations else None
            return state

        except Exception as e:
            raise RuntimeError(f"Error extracting throw-stage combinations: {e}")

    @ensure_llm
    def compressor_calculations_agent(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """
        Perform compressor calculations using predefined tools and update state with results.

        Args:
            state: EquipmentState object containing extracted data.
            llm: Optional language model instance; defaults to self.llm.

        Returns:
            EquipmentState: Updated state with calculation results.

        Raises:
            RuntimeError: For errors during tool execution or LLM processing.
        """
        try:
            tools = [
                head_end_area,
                crank_end_area,
                head_end_displacement,
                crank_end_displacement,
                swept_volume,
                head_end_clearances,
                crank_end_clearances,
                mean_piston_speed,
                he_suction_valve_diameter,
                he_discharge_valve_diameter,
                ce_suction_valve_diameter,
                ce_discharge_valve_diameter,
            ]
            results = {}
            prompt = self.prompt_manager.get_langchain_prompt(recip_tool_call_prompt)

            for tool in tools:
                prompt_str = prompt.format(
                    input_dict=state.dict_from_markdown,
                    tool_name=tool.name,
                    tool_args=tool.args,
                    tool_description=tool.description,
                )
                try:
                    chain = llm | JsonOutputParser()
                    json_output = chain.invoke(prompt_str)
                    result = tool.invoke(json_output)
                    payload = {
                        key: {"unit": "", "value": value}
                        for key, value in result.items()
                    }
                    state.dict_from_markdown.update({tool.name: payload})
                    results[tool.name] = result
                except Exception as e:
                    results[tool.name] = f"Error: {str(e)}"

            state.calculation_results = results
            return state
        except Exception as e:
            raise RuntimeError(f"Error in compressor calculations: {e}")

    @ensure_llm
    def update_base_config_node(
        self, state: EquipmentState, llm: str = None
    ) -> EquipmentState:
        """
        Update the base configuration with calculation results using LLM and save the final config.

        Args:
            state: EquipmentState object containing base config and calculation results.
            llm: Optional language model instance; defaults to self.llm.

        Returns:
            EquipmentState: Updated state with final configuration.

        Raises:
            RuntimeError: For errors during LLM processing or validation.
        """
        try:
            prompt = self.prompt_manager.get_langchain_prompt(final_mapping_prompt)
            base_config_dict = (
                json.loads(state.base_config) if state.base_config else {}
            )  # Parse JSON string
            prompt_str = prompt.format(
                base_config=(
                    base_config_dict["data"]
                    if "data" in base_config_dict
                    else base_config_dict
                ),  # Extract 'data' or use dict
                calculated_params=state.calculation_results,
                format_instructions=PydanticOutputParser(
                    pydantic_object=OutputDataValidator
                ).get_format_instructions(),
            )
            chain = llm | StrOutputParser()
            final_config = chain.invoke(prompt_str)
            validated_response = OutputDataValidator.model_validate_json(final_config)
            state.final_config = final_config  # Store JSON string
            file_name = (
                state.required_stage_throw.replace("->", "_").replace(" ", "_")
                if state.required_stage_throw
                else "default"
            )
            save_config_to_file(validated_response.data, file_name)  # Use dict for file
            return state
        except Exception as e:
            raise RuntimeError(f"Error updating base configuration: {e}")

    def process_next_combination_node(self, state: EquipmentState) -> EquipmentState:
        """Select the next throw-stage combination for processing."""
        combinations = state.throw_stage_comb or []
        current = state.required_stage_throw
        if not combinations:
            state.required_stage_throw = None
            return state
        try:
            current_index = combinations.index(current)
            if current_index < len(combinations) - 1:
                state.required_stage_throw = combinations[current_index + 1]
        except (ValueError, IndexError):
            if combinations:
                state.required_stage_throw = combinations[0]
        return state

    def check_has_more_combinations(self, state: EquipmentState) -> str:
        """Check if there are more throw-stage combinations to process."""
        combinations = state.throw_stage_comb or []
        current = state.required_stage_throw
        try:
            current_index = combinations.index(current)
            if current_index < len(combinations) - 1:
                return "more_combinations"
            return "end"
        except (ValueError, IndexError):
            return "end"

    def motor_node(self, state: EquipmentState) -> EquipmentState:
        """Handle induction motor-specific processing by clearing throw-stage combinations."""
        state.throw_stage_comb = []
        state.required_stage_throw = None
        return state

    def screw_compressor_node(self, state: EquipmentState) -> EquipmentState:
        """Handle screw compressor-specific processing by clearing throw-stage combinations."""
        state.throw_stage_comb = []
        state.required_stage_throw = None
        return state

    def centrifugal_compressor_node(self, state: EquipmentState) -> EquipmentState:
        """Handle centrifugal compressor-specific processing by clearing throw-stage combinations."""
        state.throw_stage_comb = []
        state.required_stage_throw = None
        return state

    def route_to_equipment(self, state: EquipmentState) -> str:
        """Route to the appropriate equipment-specific subgraph based on equipment name."""
        equipment_name = self.validator.equipment_name.lower()
        if "reciprocating" in equipment_name:
            return "Reciprocating_Compressor"
        elif "induction" in equipment_name:
            return "Induction_Motor"
        elif "screw" in equipment_name:
            return "Screw_Compressor"
        elif "centrifugal" in equipment_name:
            return "Centrifugal_Compressor"
        raise ValueError(f"Unknown equipment type: {equipment_name}")

    def define_edges(self):
        """Define the edges for the main workflow and subgraphs."""
        return {
            START: "route",
            "route": (
                self.route_to_equipment,
                {
                    "Reciprocating_Compressor": "Reciprocating_Compressor",
                    "Induction_Motor": "Induction_Motor",
                    "Screw_Compressor": "Screw_Compressor",
                    "Centrifugal_Compressor": "Centrifugal_Compressor",
                },
            ),
            "Reciprocating_Compressor": {
                START: "extract_pdf",
                "extract_pdf": "extract_schema",
                "extract_schema": "recip_comp",
                "recip_comp": "create_dict",
                "create_dict": "create_base_config",
                "create_base_config": "compressor_calculations",
                "compressor_calculations": "update_base_config",
                "update_base_config": (
                    self.check_has_more_combinations,
                    {"more_combinations": "process_next_combination", "end": END},
                ),
                "process_next_combination": "create_dict",
            },
            "Induction_Motor": {
                START: "extract_pdf",
                "extract_pdf": "extract_schema",
                "extract_schema": "motor",
                "motor": "create_dict",
                "create_dict": "create_base_config",
                "create_base_config": END,
            },
            "Screw_Compressor": {
                START: "extract_pdf",
                "extract_pdf": "extract_schema",
                "extract_schema": "screw_compressor",
                "screw_compressor": "create_dict",
                "create_dict": "create_base_config",
                "create_base_config": END,
            },
            "Centrifugal_Compressor": {
                START: "extract_pdf",
                "extract_pdf": "extract_schema",
                "extract_schema": "centrifugal_compressor",
                "centrifugal_compressor": "create_dict",
                "create_dict": "create_base_config",
                "create_base_config": END,
            },
        }

    def build_graph(self):
        """Build the complete workflow graph with subgraphs for each equipment type."""
        workflow = StateGraph(EquipmentState)
        workflow.add_node("route", lambda state: state)

        # Define subgraphs
        reciprocating_subgraph = StateGraph(EquipmentState)
        reciprocating_subgraph.add_node("extract_pdf", self.extract_pdf_node)
        reciprocating_subgraph.add_node("extract_schema", self.extract_schema_node)
        reciprocating_subgraph.add_node("recip_comp", self.recip_comp_node)
        reciprocating_subgraph.add_node("create_dict", self.create_dict_node)
        reciprocating_subgraph.add_node(
            "create_base_config", self.create_base_config_node
        )
        reciprocating_subgraph.add_node(
            "compressor_calculations", self.compressor_calculations_agent
        )
        reciprocating_subgraph.add_node(
            "update_base_config", self.update_base_config_node
        )
        reciprocating_subgraph.add_node(
            "process_next_combination", self.process_next_combination_node
        )

        induction_subgraph = StateGraph(EquipmentState)
        induction_subgraph.add_node("extract_pdf", self.extract_pdf_node)
        induction_subgraph.add_node("extract_schema", self.extract_schema_node)
        induction_subgraph.add_node("motor", self.motor_node)
        induction_subgraph.add_node("create_dict", self.create_dict_node)
        induction_subgraph.add_node("create_base_config", self.create_base_config_node)

        screw_subgraph = StateGraph(EquipmentState)
        screw_subgraph.add_node("extract_pdf", self.extract_pdf_node)
        screw_subgraph.add_node("extract_schema", self.extract_schema_node)
        screw_subgraph.add_node("screw_compressor", self.screw_compressor_node)
        screw_subgraph.add_node("create_dict", self.create_dict_node)
        screw_subgraph.add_node("create_base_config", self.create_base_config_node)

        centrifugal_subgraph = StateGraph(EquipmentState)
        centrifugal_subgraph.add_node("extract_pdf", self.extract_pdf_node)
        centrifugal_subgraph.add_node("extract_schema", self.extract_schema_node)
        centrifugal_subgraph.add_node(
            "centrifugal_compressor", self.centrifugal_compressor_node
        )
        centrifugal_subgraph.add_node("create_dict", self.create_dict_node)
        centrifugal_subgraph.add_node(
            "create_base_config", self.create_base_config_node
        )

        # Get edge definitions
        edges = self.define_edges()

        # Apply edges to reciprocating subgraph
        recip_edges = edges["Reciprocating_Compressor"]
        for source, target in recip_edges.items():
            if source == START:
                reciprocating_subgraph.add_edge(START, target)
            elif isinstance(target, tuple):
                reciprocating_subgraph.add_conditional_edges(
                    source, target[0], target[1]
                )
            else:
                reciprocating_subgraph.add_edge(source, target)

        # Apply edges to induction subgraph
        induction_edges = edges["Induction_Motor"]
        for source, target in induction_edges.items():
            if source == START:
                induction_subgraph.add_edge(START, target)
            else:
                induction_subgraph.add_edge(source, target)

        # Apply edges to screw subgraph
        screw_edges = edges["Screw_Compressor"]
        for source, target in screw_edges.items():
            if source == START:
                screw_subgraph.add_edge(START, target)
            else:
                screw_subgraph.add_edge(source, target)

        # Apply edges to centrifugal subgraph
        centrifugal_edges = edges["Centrifugal_Compressor"]
        for source, target in centrifugal_edges.items():
            if source == START:
                centrifugal_subgraph.add_edge(START, target)
            else:
                centrifugal_subgraph.add_edge(source, target)

        # Add subgraphs to main workflow
        workflow.add_node("Reciprocating_Compressor", reciprocating_subgraph.compile())
        workflow.add_node("Induction_Motor", induction_subgraph.compile())
        workflow.add_node("Screw_Compressor", screw_subgraph.compile())
        workflow.add_node("Centrifugal_Compressor", centrifugal_subgraph.compile())

        # Apply main workflow edges
        workflow.add_conditional_edges(
            "route", self.route_to_equipment, edges["route"][1]
        )
        workflow.set_entry_point("route")

        return workflow.compile(name="Equipment-Graph").with_config(
            {"callbacks": self.langfuse_handler}
        )

    def invoke_graph(
        self, initial_state: EquipmentState, run_name: str = "Equipment-Pipeline"
    ):
        """
        Invoke the workflow graph with the given initial state.

        Args:
            initial_state: Initial EquipmentState object to initialize the graph.
            run_name: Name of the run for logging purposes.

        Returns:
            Result of the graph execution.

        Raises:
            RuntimeError: If graph execution fails.
        """
        self.graph = self.build_graph()
        if self.logging:
            result = self.graph.invoke(initial_state)
            wait_for_all_tracers()
        else:
            result = self.graph.invoke(initial_state)
        return result

    def draw_graph(self, output_path=None) -> bytes:
        """
        Generate a visual representation of the workflow graph as a Mermaid diagram in PNG format.
        Args: output_path (Optional[str])- If provided, save the PNG image to this file path.
        Returns: bytes- PNG image data of the graph.
        """
        graph = self.build_graph()
        graph_structure = graph.get_graph(xray=2)
        png_data = graph_structure.draw_mermaid_png()
        if output_path:
            with open(output_path, "wb") as f:
                f.write(png_data)
        return png_data
