def recip_comp_dict_prompt() -> str:
    prompt = """
   You are a mechanical engineer specializing in turbomachinery data analysis.

   ## CONTEXT:
   - Equipment: Reciprocating Compressor
   - Input Markdown Text: {markdown_text}
   - Stage-Throw Combination: {combination}
   - require stage-throw combination: {require_stage_throw}
   - The Input Markdown Text is a manufacturer's datasheet for a reciprocating compressor, originally in tabular format, converted to markdown. This datasheet contains comprehensive technical specifications including compressor data, driver data, services, stage data and cylinder/throw data.

   ## TASK:
   Extract all available technical data corresponding to the specified {require_stage_throw} from the Input Markdown Text and organize it into a structured JSON format.
   

   ## REQUIREMENTS:
   **Data Structure Understanding**
   The markdown follows this hierarchical structure and extratc data accordingly:
   1. *Header Information*: Machine identification and basic specifications
   2. *Compressor & Driver Data*: General compressor and driver parameters
   3. *Tabular Data Section*: 
      - Servies, Stage Data, and Cylinder Data
      - Column headers represent stage numbers (e.g., "Stage Number 1,2, 3 ")
      - Below those Cylinder or Throw numbers (e.g., "Frame Ext/Cyl. Bore #/IN 1/26.500 3/26.500 5/26.500 2/26.500 4/15.000 6/9.500" or throw numbers "Throw 1 Throw 3 Throw 4 Throw 2")
      - if a stage data  is marked as `---`, it means the stage data is the same as the previous stage in the sequence (e.g., if Stage 1 is followed by `---`, means that column has the same data as Stage 1)
      - The first row contains stage numbers, and the second row contains throw numbers.
      - Row "Stage number at (HE/CE)" maps stages to physical positions/throws
      - Subsequent rows contain parameter values aligned to each stage-throw combination

   **Stage-Throw Mapping Logic**
   -The combination string `{combination}` defines stage-to-throw  relationships (e.g., "stage 1->throw 1, stage 1->throw 3, stage 2->throw 2")
   - The row "Stage number at (HE/CE)" provides positional alignment for parameter extraction
   - Each column position corresponds to a specific stage-throw combination

   **Extraction Requirements**
   Extract data for the specified stage-throw combination: `{require_stage_throw}`
   - Identify the correct column position using the stage-throw mapping
   - Extract all parameters from that column, from the first data row through the last parameter
   - The property/parameter should be key and the value should be a dictionary with `unit` and `value` keys
   - Ensure all parameters are captured, including those with "N/A" values

   **Data Processing Rules**
   1. Parameter Format: Recognize "parameter_name,unit numeric_value/text" structure
   2. Unit Handling: Separate units from values, including percentages and unitless parameters
   3. Missing Data: Preserve "N/A" values as string literals
   4. Completeness: Capture every parameter present in the specified column - no data should be omitted
   

   ## OUTPUT FORMAT:
   Return a single structured JSON object using the following format:
   ```json
   {{ 'data':{{
      "machine_name": "extracted_machine_name",
      "machine_type": "extracted_machine_type",
      "machine_data": {{
         "parameter_name": {{
               "unit": "unit_string",
               "value": "numeric_or_text_value"
         }}
      }},
      "stage_data": {{
         "stage_number": "extracted_stage_number",
         "stage_parameters": {{
               "parameter_name": {{
                  "unit": "unit_string",
                  "value": "numeric_or_text_value"
               }}
         }}
      }},
      "throw_data": {{
         "throw_number": "extracted_throw_number",
         "throw_parameters": {{
               "parameter_name": {{
                  "unit": "unit_string",
                  "value": "numeric_or_text_value"
               }}
         }}
      }}
   }}
   }}
   ```

   ## GUIDELINES:
   - Ensure the column corresponding to `{require_stage_throw}` is fully captured.
   - Do not omit any parameters; data completeness is mandatory.
   - Interpret markdown table structure correctly: column order is key.
   - Maintain clean separation between stage-specific and throw-specific data.
   - Keep the data types consistent and retain exact casing and structure from source.

   ## Important Note:
    - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.

   
   ## Response Format:
   {format_instructions}
   """
    return prompt


def induction_motor_dict_prompt() -> str:
    prompt = """
   You are a mechanical engineer with expertise in turbomachinery and electric motor/ induction motor configurations.

   ## CONTEXT:
   - Equipment: Induction Motor
   - Input Markdown Text: {markdown_text}
   - Stage-Throw Combination: {require_stage_throw} or not applicable to this machine
   - Mapping String: {combination} or not applicable to this machine
   - The source text is extracted from a datasheet originally formatted as a table.

   ## TASK:
   Extract and structure motor-related technical specifications from the provided markdown text into a clean JSON dictionary.

   ## REQUIREMENTS:
   1. The markdown text contains technical specifications for an induction motor, including parameters like voltage, current, power, efficiency, etc.
   2. The data is organized in a tabular format, with each parameter represented as `item' and unit as 'Item No.' etc.
   3. Extract the all parameters/items from the markdown text, including their units and values.
   4. The value can be numeric or textual (e.g., "N/A").
   5. If the value is `"N/A"`, preserve it as a string literal.
   6. Separate the `unit` and `value` for each parameter
   7. If the value is `"N/A"` or '-', preserve it as a string literal or "N/A"
   8. Organize the extracted parameters under the `motor_data` section
   9. Add metadata at the top level:
      - `machine_name`: Extracted if present in the text
      - `machine_type`: Set as `"motor"`

   ## OUTPUT FORMAT:
   Return the final dictionary as:
   {{"data": {{
      "machine_name": "string",
      "machine_type": "Induction Motor",
      "motor_data": {{
         "parameter_name": {{
               "unit": "unit_string",
               "value": "numeric_or_text_value"
            }}
         }}
      }}
   }}

   ## GUIDELINES:
   - Maintain the original order of parameters as they appear in the text
   - Preserve numeric values as numbers and textual values (including "N/A") as strings
   - Do not omit any parameters present in the input text

   ## Important Note:
   - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.

   ## Response Format:
   {format_instructions}
   """
    return prompt


def centri_comp_dict_prompt() -> str:
    prompt = """
    You are a mechanical engineer with expertise in turbomachinery and centrifugal compressor configurations.

    ## CONTEXT:
    - Equipment: Centrifugal Compressor
    - Input Markdown Text: {markdown_text}
    - Stage-Throw Combination: {require_stage_throw}
    - Mapping String: {combination}
    - The source text is extracted from a datasheet originally formatted as a table.

    ## TASK:
    Extract and structure centrifugal compressor technical specifications from the provided markdown text into a clean JSON dictionary.

    ## REQUIREMENTS:
    1. Identify all parameters in the format: `parameter_name,unit value`
    2. Separate the `unit` and `value` for each parameter
    3. If the value is `"N/A"`, preserve it as a string literal
    4. Organize the extracted parameters under the `compressor_data` section
    5. Add metadata at the top level:
       - `machine_name`: Extracted if present in the text
       - `machine_type`: Set as `"centrifugal_compressor"`

    ## OUTPUT FORMAT:
    Return the final dictionary as:
    {
        "machine_name": "string",
        "machine_type": "centrifugal_compressor",
        "compressor_data": {
            "parameter_name": {
                "unit": "unit_string",
                "value": "numeric_or_text_value"
            }
        }
    }

    ## GUIDELINES:
    - Maintain the original order of parameters as they appear in the text
    - Preserve numeric values as numbers and textual values (including "N/A") as strings
    - Do not omit any parameters present in the input text

    ## Important Note:
    - Respond only with a raw JSON string.
    - Do not include triple backticks, markdown formatting, or any extra explanation.

    ## Response Format:
    {format_instructions}
    """
    return prompt


def screw_comp_dict_prompt() -> str:
    prompt = """
   You are a mechanical engineer with expertise in turbomachinery and screw compressor configurations.

   ## CONTEXT:
   - Equipment: Screw Compressor
   - Input Markdown Text: {markdown_text}
   - Stage-Throw Combination: {require_stage_throw} or not applicable to this machine
   - Mapping String: {combination} or not applicable to this machine
   - The source text is extracted from a datasheet originally formatted as a table.

   ## TASK:
   Extract and structure screw compressor technical specifications from the provided markdown text which has multiple page data into a clean JSON dictionary.

   ## REQUIREMENTS:
   1. Identify all Sections  in the Markdown text: `Gas Analysis`,'Suction Conditions',"Discharge Conditions", `Compressor Performance`,"Compressor Data  etc.
   2. Do not consider the `Testing and inspection requirements`, 'Drawing and data requirements','Mechanical characteristics' section for extraction.
   2. Separate the `unit` and `value` for each parameter
   3. If the value is `"N/A"`, preserve it as a string literal
   4. Organize the extracted parameters under the `compressor_data` section
   5. Add metadata at the top level:
      - `machine_name`: Extracted if present in the text
      - `machine_type`: Set as `"screw compressor"`

## OUTPUT FORMAT:
   Return the final dictionary as:
   {{"data": {{
      "machine_name": "string",
      "machine_type": "Screw Compressor",
      "motor_data": {{
         "parameter_name": {{
               "unit": "unit string",
               "value": "numeric or text value"
            }}
         }}
      }}
   }}

   ## GUIDELINES:
   - Maintain the original order of parameters as they appear in the text
   - Preserve numeric values as numbers and textual values (including "N/A") as strings
   - Do not omit any parameters present in the input text

   ## Important Note:
   - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.

   ## Response Format:
   {format_instructions}
   """
    return prompt


def data_mapping_prompt() -> str:
    prompt = """
   You are a mechanical engineer with expertise in turbomachinery. 

   ## CONTEXT:
   - Equipment: {equipment_name}
   - Source Dictionary:{data_sheet_dict}
   - Target Dictionary:{config_schema_dict}
   
   ### Dictionary Descriptions:
   **Source Dictionary**
   - This dictionary contains structured {equipment_name} data.
   - It has top-level keys such as: `machine_name`, `machine_type`, `machine_data` and so on.
   - Each top-level key maps to a nested dictionary, where each property has value against it in the format: {{"unit": "psig", "value": 156.41}}
   
   **Target Dictionary**
   - This is a configuration schema where:
   - Keys are predefined configuration parameters.
   - Values are either `null`,'None', numeric, string, boolean, or empty list (empty or filled).
   - Some keys require values in `list[]` format (e.g., compositions, curves).


   ## TASK:
   You are provided with two dictionaries. Your task is to intelligently map values from one dictionary 'data_sheet_dict' to another  based on semantic similarity and relevance based on technical term. Populate the `config_schema_dict` by intelligently extracting and assigning values from the `data_sheet_dict`.

   ## REQUIREMENTS:
   1. Iterate through each key in the  `config_schema_dict`.
   2. Search for the corresponding key in the `data_sheet_dict` based on naming, technical similarity, and turbomachinery domain knowledge and extract the value. for example:
   - If `config_schema_dict` has a key like `"stroke"` and `data_sheet_dict` has a key like `"stroke_length"`, you should map the value from `data_sheet_dict["stroke_length"]` to `config_schema_dict["stroke"]`.
   - The value contains a dictionary with two keys: "unit" and "value". For example, if the value in `data_sheet_dict` is `{{"unit": "in", "value": 6.5}}`, you should extract the value 6.5 and assign it to the key of 'config_schema_dict'.
   3. If a confident match of the key is found based on naming, technical similarity, and turbomachinery domain knowledge only the update the value in `config_schema_dict` with the value from `data_sheet_dict`.
   4. If no confident match is found:
   - Leave the original key-value as it is in `config_schema_dict` unchanged.
      

   ## GUIDELINES:
   - This task involves domain knowledge of {equipment_name} and their configurations—ensure mappings are technically sound and similary using mechanical and turbomachinery domain.
   - Only update keys when you're reasonably certain about the mapping.
   - Preserve keys in `config_schema_dict` that were not updated as it is.
   - do not remove any keys from `config_schema_dict` even if they are not present in `data_sheet_dict`.
   - Return the updated `config_schema_dict` as a JSON object without removing any key from it.
   
   ## Example Output:
   -  Below is a sample/example of what the `config_schema_dict` may look like after mapping :
   config_schema_dict ={{data: {{
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
   }}
   

   ## Important Note:
   - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.

   ## Response Format: 
   {format_instructions}
   
   """
    return prompt


def recip_stage_throw_extraction_prompt() -> str:
    prompt = """
   You are a mechanical engineer with expertise in turbomachinery, specializing in parsing datasheet documentation for reciprocating compressors.

   ## CONTEXT:
   - Source: {markdown_text}
   - Focus: Extraction of stage and throw combinations from the provided markdown text.

   ## TASK:
   Extract the stage and throw mapping from the provided markdown text.

   ## REQUIREMENTS:
   1. Identify the line starting with `Stage number at (HE/CE)` to extract stage information.
      - Example: `Stage number at (HE/CE) 1/1 1/1 1/1 2/2 3/3 4/4` → each X/X pair represents a stage.
   2. Identify the line starting with `Frame Ext/Cyl. Bore` to extract throw information.
      - Example: `Frame Ext/Cyl. Bore #/IN 1/26.500 3/26.500 5/26.500 2/26.500 4/15.000 6/9.500` → numbers before `/` are throw numbers.
   3. Each stage corresponds to the throw at the same position in their respective lines.
   4. If a stage is marked as `---`, it means the stage is the same as the previous stage in the sequence (e.g., if Stage 1 is followed by `---`, the `---` is also Stage 1)
   5. The final output should map each stage to its throw in the format:
      - `"stage 1->throw 1, stage 1->throw 3, stage 2->throw 4, stage 3->throw 2"`

   ##Example of Input Stage and Throw Data these data are the two lines from the selected markdown file :
   - Example 1.  Data present in Markdown text: 
                  Stage Data: 1 --- 2 3
                  Cylinder Data: Throw 1 Throw 3 Throw 4 Throw 2 
               Output: stage 1->throw 1, stage 1->throw 3, stage 2->throw 4, stage 3->throw 2

   - Example 2.  Data present in Markdown text :
                  Stage Number    1          2          3          4 
                  Stage number at (HE/CE)    1/1        1/1        1/1        2/2        3/3        4/4 
                  Frame Ext/Cyl. Bore        #/IN  1/26.500   3/26.500   5/26.500   2/26.500   4/15.000   6/ 9.500
               Output: stage 1->throw 1, stage 1->throw 3, stage 1->throw 5, stage 2->throw 2, stage 3->throw 4, stage 4->throw 6

   ## GUIDELINES:
   - Output only the extracted combinations.
   - Do not return any explanation, heading, or formatting.
   - Maintain the order as found in the input data.

   ## Important Note:
   - Respond only with the final string in the format: "stage X->throw Y, ...". Do not include triple backticks or any markdown.

   
   """
    return prompt


def recip_tool_call_prompt() -> str:
    prompt = """
   You are a mechanical engineer and agentic tooling expert specializing in parameter mapping for function calls in turbomachinery applications.

   ## CONTEXT:
   - Function Name: {tool_name}
   - Function Description: {tool_description}
   - Required Parameters: {tool_args}
   - Input Dictionary: {input_dict}

   ## TASK:
   Map values from the input dictionary to the parameters of the function `{tool_name}` and return the final argument mapping as a JSON object.

   ## REQUIREMENTS:
   1. Analyze the function signature and docstring to understand the expected parameters.
   2. Match keys from `input_dict` to the function parameters in `{tool_args}` using:
      - **Direct Match**: Exact string match (e.g., `bore_dia_in` → `bore_dia_in`)
      - **Semantic Match**: Use domain knowledge to match similar terms, e.g.:
      - `bore_dia_in` could match `cylinder_bore_diameter`, `cyl_bore_dia`, `cylinder_bore_dia`
      - Consider abbreviations, synonyms, and turbomachinery domain terminology.

   3. Extract values from the matched keys and ensure correct formatting as per parameter expectations.
   4. Handle missing parameters using function defaults if available; otherwise, flag as missing or exclude from the result.

   ## GUIDELINES:
   - Prioritize precision: only map when confident in similarity.
   - Maintain consistency with expected data types and formatting.
   - Do not modify or guess undefined values.
   - Units can be ignored unless required for accurate interpretation.

   ## OUTPUT:
   - Respond only with a raw JSON string containing the final mapped parameters.
   - Do not include any explanation, triple backticks, or markdown formatting.

   """
    return prompt


def final_mapping_prompt() -> str:
    prompt = """
   You are a configuration mapping expert for turbomachinery systems.

   ## CONTEXT:
   - Base Configuration: {base_config}
   - Calculated Parameters: {calculated_params}

   ## TASK:
   Map the calculated parameters to the most appropriate fields in the base configuration to produce the `final_config`.

   ## REQUIREMENTS:
   1. Use similarity in meaning to match keys. Example: "head_end_area" might map to "head_end_area_in" or "he_area".
   2. If a calculated parameter does not have a relevant match in the base config, leave the base configuration unchanged for that parameter.
   3. The goal is to update the base config with as many meaningful and accurate mappings from the calculated parameters as possible.

   ## GUIDELINES:
   - Ensure the final output is a valid JSON object representing the updated `final_config`.
   - Do not include any additional text, markdown formatting, or explanation.
   - Only output the raw JSON string of the updated configuration.
   - exapmple of a valid JSON output:
   final_config = {{data:
   {{
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
   }}

   ## Important Note:
   - Respond only with a raw JSON string. Do not include triple backticks or markdown formatting.
   
   
   ## Response Format:
   {format_instructions}
   """
    return prompt
