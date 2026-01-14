import os
import json
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

_cached_model = None

def _get_available_model():
    """Fetches and caches the best available Gemini model."""
    global _cached_model
    if _cached_model:
        return _cached_model

    if not GEMINI_API_KEY:
        return None

    try:
        models = genai.list_models()
        preferred_order = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-pro",
        ]
        available = [
            m.name.replace("models/", "")
            for m in models
            if "generateContent" in m.supported_generation_methods
        ]
        for model in preferred_order:
            if model in available:
                _cached_model = model
                return model
        return None
    except Exception as e:
        # Log the exception for debugging, but don't expose it directly.
        print(f"ERROR: Could not list Gemini models: {e}")
        return None

def generate_ai_analysis(prompt):
    """Generates security analysis using a Gemini model, ensuring JSON output."""
    if not GEMINI_API_KEY:
        return {
            "status": "error",
            "error_type": "misconfigured",
            "message": "No Gemini API key configured.",
        }

    model_name = _get_available_model()
    if not model_name:
        return {
            "status": "error",
            "error_type": "model_unavailable",
            "message": "No suitable models available.",
        }

    json_instruction = """
    IMPORTANT: Your entire response MUST be a single, valid JSON object.
    Do not include any text, notes, or explanations before or after the JSON.
    Do not use markdown formatting (e.g., ```json).

    The JSON object must conform to the following schema:
    {
      "executive_summary": "string",
      "architecture": "string",
      "threat_model": "string",
      "secure_sdlc": "string",
      "cost_estimation": "string",
      "testing_plan": "string",
      "likelihood_score": "integer (1-5)",
      "impact_score": "integer (1-5)",
      "risk_adjustment": "integer (-30 to +30)",
      "key_risks": ["string"],
      "recommendations": ["string"]
    }
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
        # The response.text is already a JSON string, so we parse it to a Python dict
        return json.loads(response.text)
    except Exception as e:
        return {
            "status": "error",
            "error_type": "ai_error",
            "message": f"AI Error: {str(e)}",
        }
