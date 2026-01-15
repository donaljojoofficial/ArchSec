import os
import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Define the single, allowed Gemini model for this application.
ALLOWED_MODELS = ["models/gemini-2.5-flash"]

def generate_ai_analysis(prompt):
    """
    Generates security analysis using the mandated Gemini 2.5 Flash model.

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

    genai.configure(api_key=api_key)

    # Enforce the use of the specified Gemini model.
    model_name = "models/gemini-2.5-flash"
    
    if model_name not in ALLOWED_MODELS:
        # This is a hard failure because the application is misconfigured.
        raise RuntimeError(f"Invalid Gemini model: '{model_name}'. Allowed models are: {ALLOWED_MODELS}")

    logger.info(f"Using Gemini model: {model_name}")
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
        logger.info("Sending request to Gemini API...")
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(
            full_prompt, generation_config=generation_config
        )
        
        logger.info("Gemini response received successfully.")
        # The response.text is a JSON string, which we load into a Python dict.
        ai_response_dict = json.loads(response.text)
        return True, ai_response_dict

    except Exception as e:
        logger.exception("Gemini API failure") # exc_info=True is implicit with logger.exception
        return False, {
            "status": "error",
            "error_type": "api_error",
            "message": str(e),
        }
