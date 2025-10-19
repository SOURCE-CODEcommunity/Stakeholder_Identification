import re
import json

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be saved to 'app.log'
    filemode='a'  # Append to the log file instead of overwriting
)
logger = logging.getLogger(__name__)

def clean_with_regex(raw_string):
    """
    Use regex to extract quoted strings from the malformed data
    """
    # Find all quoted strings
    pattern = r'"([^"]+)"'
    matches = re.findall(pattern, raw_string)
    
    # Filter out non-content matches (like 'json', etc.)
    content_items = []
    for match in matches:
        # Skip short items that are likely formatting artifacts
        if len(match) > 10 and not match in ['json']:
            content_items.append(match)
    
    return content_items





# def clean_ai_json_response(raw_response: str):
#     """
#     Cleans AI-generated response that may include markdown code blocks
#     and returns a proper Python dict.
#     """
#     # Join list if the response is a list
#     if isinstance(raw_response, list):
#         raw_response = "".join(raw_response)

#     # Remove ```json and ``` code block markers
#     cleaned = re.sub(r"```(?:json)?", "", raw_response, flags=re.IGNORECASE).strip()

#     # Sometimes there are extra newlines at start/end
#     cleaned = cleaned.strip()
#     logger.info(f"Cleaned Gemini Stakeholders Extract: {cleaned}")


#     # Load as JSON
#     try:
#         data = json.loads(cleaned)
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#         logger.error(f"Error decoding JSON from \"clean_ai_json_response\" function in utils.py: {str(e)}")
#         return None

#     return data






def clean_ai_json_response(raw_list):
    """
    Cleans AI-generated response and always returns a list of JSON dicts.
    Handles ```json fenced blocks and both single/multiple JSON objects.
    """
    all_stakeholders = []

    for block in raw_list:
        # 1️⃣ Extract JSON part between ```json and ```
        match = re.search(r"```json\s*(\{.*?\})\s*```", block, re.DOTALL)
        if match:
            json_str = match.group(1)

            # 2️⃣ Parse JSON string into dict
            try:
                data = json.loads(json_str)
                # 3️⃣ Append stakeholders to the big list
                if "stakeholders" in data:
                    all_stakeholders.extend(data["stakeholders"])
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

    # 4️⃣ Build the combined dictionary
    combined = {"stakeholders": all_stakeholders}

    return combined

