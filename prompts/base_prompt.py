receip_data_extraction_prompt = """# Turbomachinery Data Extraction Prompt

## Input Data
The markdown text to process:
```
{text}
```

You are a mechanical engineer specializing in turbomachinery analysis. Your objective is to comprehensively extract and structure all data from the provided markdown text into a complete JSON dictionary format.

## Context
The source material is a manufacturer's datasheet for a reciprocating compressor, originally in tabular format, converted to markdown. This datasheet contains comprehensive technical specifications including compressor configuration, driver specifications, stage parameters, throw/cylinder data, and service conditions.

## Data Structure Understanding
The markdown follows this hierarchical structure:
1. **Header Information**: Machine identification and basic specifications
2. **Compressor & Driver Data**: General machine parameters
3. **Tabular Data Section**: 
   - Column headers represent stage numbers (e.g., "Stage Number 1 2 3 4")
   - Row "Stage number at (HE/CE)" maps stages to physical positions/throws
   - Subsequent rows contain parameter values aligned to each stage-throw combination

## Stage-Throw Mapping Logic
- The combination string `{combination}` defines stage-to-throw relationships (e.g., "stage 1->throw 1, stage 1->throw 3, stage 2->throw 2")
- The row "Stage number at (HE/CE)" provides positional alignment for parameter extraction
- Each column position corresponds to a specific stage-throw combination

## Extraction Requirements

### Scope
Extract data for the specified stage-throw combination: `{require_stage_throw}`
- Identify the correct column position using the stage-throw mapping
- Extract all parameters from that column, from the first data row through the last parameter

### Data Processing Rules
1. **Parameter Format**: Recognize "parameter_name,unit numeric_value/text" structure
2. **Unit Handling**: Separate units from values, including percentages and unitless parameters
3. **Missing Data**: Preserve "N/A" values as string literals
4. **Completeness**: Capture every parameter present in the specified column - no data should be omitted

### Output Structure
Generate a comprehensive JSON dictionary with this structure:
```json
data = {{
    "machine_name": "extracted_machine_name",
    "machine_type": "extracted_machine_type", 
    "machine_data": {{
        "general_parameter_1": {{
            "unit": "unit_string",
            "value": "numeric_or_text_value"
        }},
        "general_parameter_2": {{
            "unit": "unit_string", 
            "value": "numeric_or_text_value"
        }}
    }},
    "stage_data": {{
        "stage_number": "extracted_stage_number",
        "stage_parameters": {{
            "parameter_1": {{
                "unit": "unit_string",
                "value": "numeric_or_text_value"
            }}
        }}
    }},
    "throw_data": {{
        "throw_number": "extracted_throw_number",
        "throw_parameters": {{
            "parameter_1": {{
                "unit": "unit_string", 
                "value": "numeric_or_text_value"
            }}
        }}
    }}
}}
```

## Critical Instructions
- **Table Structure Recognition**: Analyze the markdown carefully to understand column-row relationships before extraction
- **Position Accuracy**: Use the "Stage number at (HE/CE)" row as the definitive guide for column positioning
- **Data Completeness**: Every parameter in the target column must be included in the output
- **Format Compliance**: Return only raw JSON without markdown formatting or code blocks

"""

induction_data_extraction_prompt = """
You are a mechanical engineer with expertise in turbomachinery. Your task is to extract and structure motor-related configuration data from the provided markdown text (.md file) into a structured dictionary format.

The original data (extracted_text.md, a datasheet provided by the manufacturer) was in a tabular format with rows and columns.

**Instructions:**
1. The markdown text includes numeric values and descriptive data for the motor, such as model, frame size, rated power,     voltage, current, speed, frequency, efficiency, and other technical specs.
2. Each parameter is followed by its unit and value, in the format "parameter_name,unit value".
3. Include parameters with value `N/A` in the dictionary, setting their value as `"N/A"`.
4. Convert the extracted data into a structured dictionary like below:
    {{
        "machine_name": "string",
        "machine_type": "motor",
        "motor_data": {{
            "parameter_1": {{
                "unit": "unit_string",
                "value": 0.0
            }},
            "parameter_2": {{
                "unit": "unit_string",
                "value": 0.0
            }}
        }}
    }}

**Important Note:**
  - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.

**Input Data:**```
Here is the text data extracted from the PDF in markdown format:
{text}
"""

data_mapping_prompt = """
You are a mechanical engineer with expertise in turbomachinery. You are provided with two dictionaries containing {equipment_name} configuration data. Your task is to intelligently map values from one dictionary (source) to another (target) based on semantic similarity and relevance based on technical term.

### Dictionary Descriptions:
**Dictionary 1: {data_sheet_dict}**
- This dictionary contains structured {equipment_name} data.
- It has top-level keys such as: `machine_name`, `machine_type`, `machine_data` and so on.
- Each top-level key maps to a nested dictionary, where each property has value against it in the format: {{"unit": "psig", "value": 156.41}}.

**Dictionary 2: {config_schema_dict}**
- This is a configuration schema where:
- Keys are predefined configuration parameters.
- Values are either `null`, numeric, string, boolean, or lists (empty or filled).
- Some keys require values in `list[]` format (e.g., compositions, curves).

### Task Description:

Your goal is to populate the `config_schema_dict` by extracting and assigning values from `data_sheet_dict`. Follow the steps below:

#### Steps:
1. Iterate through each property (key-value pair) within the nested structure of `data_sheet_dict`.
2. For each property:
  - Extract its value (ignore the "unit").
  - Attempt to find a semantically matching key in `config_schema_dict`.
3. If a **confident match** is found (based on identical or very similar naming and meaning in scientific and technical term of turbomachine and fluid mechanics):
  - Update the corresponding key in `config_schema_dict` with the extracted value.
4. If no confident match is found, **leave the key in `config_schema_dict` unchanged**.

### Additional Instructions:
- This task involves domain knowledge of {equipment_name} and their configurations—ensure mappings are technically sound.
- Only update keys when you're reasonably certain about the mapping.
- Preserve keys in `config_schema_dict` that were not updated.
- Maintain the data types expected by the schema (e.g., if a list is expected, ensure the value is a list).
- The unit of the values should only be considered if necessary for interpretation (e.g., converting inches to mm).

**Example Output**:
Below is a sample of what the `config_schema_dict` may look like after mapping :
Note: Only return the updated `config_schema_dict` without any additional text or explanation and extra context.

  
config_schema_dict = {{
  "eos": "REFPROP",
  "stroke": 6.5,
  "da_curves": [],
  "application": "Variable Speed",
  "composition": [],
  "config_speed": 1000,
  "rod_diameter": 2.5,
  "oil_lubricated": true,
  ...
}}

**Important Note:**
- Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.
        
"""

remaining_key_prompt = """
You are a data analyst tasked with analyzing a JSON object to identify keys that are not filled, blank, or null.

**Instructions:**

1. Analyze the provided JSON object.
2. Identify keys where the value is:
   - `null`
   - An empty list (`[]`)
   - An empty string (`""`)
3. Output only a list of the keys (as strings) that meet the above criteria, in the format: `["key1", "key2", "key3"]`.
4. Do not include any additional text, explanation, or context beyond the list.

**Input Data:** {text}
"""

final_mapping_prompt = """
        You are provided with a base configuration in JSON format: {base_config}.
        You also have calculated parameters: {calculated_params}.
        Your task is to map the calculated parameters to the appropriate fields in the base configuration.
        The keys in the calculated parameters may not match exactly but should be mapped to similar fields 
        (e.g., "head_end_area" might map to "head_end_area_in" or "he_area").
        If a parameter cannot be mapped, do nothing leave it as it is".
        Return the final_config as a as explained in the below.
        
        **Example Output**:
        Below is a sample of what the `final_config` may look like after mapping :
        Note: Only return the updated `final_config` without any additional text or explanation and extra context.
        
          
        final_config = {{
          "eos": "REFPROP",
          "stroke": 6.5,
          "da_curves": [],
          "application": "Variable Speed",
          "composition": [],
          "config_speed": 1000,
          "rod_diameter": 2.5,
          "oil_lubricated": true,
          ...
        }}
        
        **Important Note:**
        - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.
        
        """


dynamic_tool_call_prompt = """
            # Function Parameter Mapping Task

            You are given an input dictionary containing various key-value pairs and need to call the function {tool_name} with the correct parameters.

            ## Your Task

            1. **Analyze the {tool_description}**: Review the docstring and signature of `{tool_name}` to understand its required parameters: `{tool_args}`

            2. **Map dictionary keys to function parameters**: For each required parameter in `{tool_args}`, find the corresponding key in `{input_dict}` using:
              - **Direct matching**: Exact key name matches (e.g., `bore_dia_in` → `bore_dia_in`)
              - **Semantic matching**: Keys with similar meaning but different naming conventions:
                - `bore_dia_in` could match `cylinder_bore_diameter`, `cyl_bore_dia`, `cylinder_bore_dia`
                - Consider common abbreviations, synonyms, and domain-specific terminology

            3. **Extract and format**: Retrieve the values from the matched keys and format them according to the function's parameter requirements

            4. **Execute**: Call `{tool_name}` with the properly mapped and formatted parameters

            ## Matching Strategy
            - Start with exact string matches
            - Use semantic similarity for partial matches (abbreviations, synonyms, domain terms)
            - Consider parameter data types and units when mapping
            - Handle missing parameters appropriately (use defaults if available, or flag as missing)
            
            ## Output:
            Output should be a JSON object with the mapped parameters in the format:
            
            ## Important Note:
            - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.
            
            ```json
            {{
              arg1 :value1,
              arg2 :value2,
              arg3 :value3,
            }}
            ```
            
            Your goal is to successfully bridge the gap between the available data keys and the function's expected parameters through intelligent key matching and value extraction.
              """
