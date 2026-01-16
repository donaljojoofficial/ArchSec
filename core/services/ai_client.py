import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

_cached_model = None


def _get_available_model():
    """
    Fetches and caches the best available model that supports content generation.
    """
    global _cached_model
    if _cached_model:
        return _cached_model

    if not GEMINI_API_KEY:
        return "ERROR: Gemini API key not configured."

    try:
        models = genai.list_models()
        # Find the best model that supports 'generateContent'
        for model in sorted(
            (m.name for m in models),
            key=lambda x: ("gemini-pro" not in x, "gemini-flash" not in x),
        ):
            if "generateContent" in genai.get_model(model).supported_generation_methods:
                _cached_model = model
                return model
        return "ERROR: No suitable model found."
    except Exception as e:
        return f"ERROR: Failed to list models - {e}"


def generate_ai_analysis(prompt):
    """
    Generates AI analysis for a given prompt and returns a structured response.

    Args:
        prompt (str): The input prompt for the AI model.

    Returns:
        tuple: A tuple containing:
            - bool: True if the analysis was successful, False otherwise.
            - dict: A dictionary containing the AI's response or an error message.
    """
    if not GEMINI_API_KEY:
        return False, {"message": "No Gemini API key configured."}

    model_name = _get_available_model()
    if model_name.startswith("ERROR:"):
        return False, {"message": model_name}

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        # Pre-process the response to handle markdown and extract JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        # Attempt to parse the cleaned text as JSON
        return True, json.loads(raw_text)

    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text with an error message
        return False, {
            "message": "AI returned a non-JSON response.",
            "raw_response": response.text,
        }
    except Exception as e:
        # Handle other exceptions from the API or processing
        return False, {"message": f"An unexpected error occurred: {e}"}

