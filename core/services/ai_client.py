import os
import json

try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_AVAILABLE:
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
    
    if not GEMINI_AVAILABLE:
        return "ERROR: google-generativeai is not installed."

    try:
        models = genai.list_models()
        
        # Sort models to prefer 'gemini-flash' and 'gemini-pro'
        sorted_models = sorted(models, key=lambda m: ("gemini-flash" not in m.name, "gemini-pro" not in m.name))
        
        for model in sorted_models:
            if "generateContent" in model.supported_generation_methods:
                _cached_model = model.name # Cache the name
                return _cached_model
        
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
    if not GEMINI_AVAILABLE:
        return False, {"message": "The AI analysis feature is unavailable because the 'google-generativeai' package is not installed."}
    
    if not GEMINI_API_KEY:
        return False, {"message": "No Gemini API key configured."}

    model_name = _get_available_model()
    if model_name.startswith("ERROR:"):
        return False, {"message": model_name}

    try:
        model = genai.GenerativeModel(model_name)
        
        # Enforce JSON output from the model
        generation_config = genai.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=generation_config)

        # The response should be a valid JSON string now.
        return True, json.loads(response.text)

    except json.JSONDecodeError:
        # This is less likely to happen, but good to keep as a fallback.
        return False, {
            "message": "AI returned a non-JSON response, even when JSON was requested.",
            "raw_response": response.text,
        }
    except Exception as e:
        # Handle other exceptions from the API or processing
        return False, {"message": f"An unexpected error occurred: {e}"}

