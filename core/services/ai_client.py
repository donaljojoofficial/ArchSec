import os
import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_ai_analysis(prompt):
    """
    Generates security analysis using the Gemini 1.5 Pro model.

    Args:
        prompt (str): The input prompt for the AI model.

    Returns:
        tuple: A tuple containing:
            - bool: True if the API call was successful, False otherwise.
            - dict: If successful, the JSON response from the AI.
                    If unsuccessful, a dictionary with error details.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        logger.error("GEMINI_API_KEY not configured.")
        return False, {
            "status": "error",
            "error_type": "config",
            "message": "GEMINI_API_KEY not configured.",
        }

    logger.info("GEMINI_API_KEY is configured.")
    genai.configure(api_key=api_key)

    model_name = "models/gemini-1.5-pro"
    logger.info(f"Sending request to Gemini API using model: {model_name}")
    logger.debug(f"Prompt size: {len(prompt)} characters")

    # This instruction should be part of the prompt engineering in the calling view,
    # but is kept here for now to minimize refactoring scope.
    json_instruction = """
    IMPORTANT: Your entire response MUST be a single, valid JSON object.
    Do not include any text, notes, or explanations before or after the JSON.
    Do not use markdown formatting (e.g., ```json).
    """

    full_prompt = f"{prompt}\n\n{json_instruction}"

    try:
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(
            full_prompt, generation_config=generation_config
        )
        
        logger.info("Successfully received response from Gemini API.")
        # The response.text is a JSON string, which we load into a Python dict.
        ai_response_dict = json.loads(response.text)
        return True, ai_response_dict

    except Exception as e:
        logger.error(f"Gemini API call failed: {e}", exc_info=True)
        return False, {
            "status": "error",
            "error_type": "api_error",
            "message": str(e),
        }
