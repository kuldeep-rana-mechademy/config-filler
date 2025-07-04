from graph.graph import EquipmentGraph
from models.model import InputDataValidator
from models.state import EquipmentState
from langchain_openai import AzureChatOpenAI
import os
from rich import print as pp
import gradio as gr

# Initialize LLM
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    openai_api_version="2025-01-01-preview",
    azure_endpoint="https://mech-llm-prod.openai.azure.com/",
    api_key=os.environ.get("OPENAI_KEY"),
    model="gpt-4o",
    temperature=0.7,
)

# Valid equipment types for the dropdown
EQUIPMENT_TYPES = [
    "reciprocating compressor",
    "induction motor",
    "screw compressor",
    "centrifugal compressor",
]


def run_equipment_graph(pdf_file, equipment_type):
    """Run the EquipmentGraph workflow and return the final base config."""
    if not pdf_file or not equipment_type:
        return "Please upload a PDF and select an equipment type."

    # Initialize state with minimal data (PDF will be processed in the graph)
    initial_state = EquipmentState()

    # Validate and create InputDataValidator instance with the temporary PDF path
    try:
        validator = InputDataValidator(
            equipment_name=equipment_type,
            pdf_path=pdf_file.name,  # Temporary path of the uploaded PDF
            constant_params={},  # Placeholder, can be extended if needed
        )
    except ValueError as e:
        return f"Validation error: {str(e)}"

    # Initialize and run the graph
    final_graph = EquipmentGraph(
        state=initial_state, validator=validator, llm=llm, logging=True
    )
    try:
        result_state = final_graph.invoke_graph(initial_state)
        final_config = (
            result_state.final_config
            if result_state.final_config
            else "No final config generated."
        )
        return str(final_config)  # Convert to string for Gradio display
    except Exception as e:
        return f"Error running graph: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Equipment Config Generator") as demo:
    gr.Markdown("# Equipment Configuration Generator")

    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF Datasheet", type="file")
            equipment_dropdown = gr.Dropdown(
                choices=EQUIPMENT_TYPES,
                label="Select Equipment Type",
                value=EQUIPMENT_TYPES[0],  # Default to first option
            )
            run_button = gr.Button("Generate Config")
        with gr.Column():
            output_text = gr.Textbox(
                label="Final Base Configuration", lines=10, interactive=False
            )

    run_button.click(
        fn=run_equipment_graph,
        inputs=[pdf_input, equipment_dropdown],
        outputs=output_text,
    )

# Launch the app
demo.launch(server_name="0.0.0.0", server_port=7860)
