import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

GEMINI_IMPORT_ERROR = None
try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
    try:
        logger.info(f"google-generativeai version: {genai.__version__}")
    except AttributeError:
        pass
except ImportError as e:
    GEMINI_AVAILABLE = False
    GEMINI_IMPORT_ERROR = str(e)
    logger.warning(f"Failed to import google.generativeai: {e}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


def parse_json_response(text_response):
    text_response = text_response.strip()
    if text_response.startswith("```json"):
        text_response = text_response[7:].strip()
    if text_response.startswith("```"):
        text_response = text_response[3:].strip()
    if text_response.endswith("```"):
        text_response = text_response[:-3].strip()
    return json.loads(text_response)


def generate_gemini_analysis(prompt):
    if not GEMINI_AVAILABLE:
        msg = "The AI analysis feature is unavailable because the 'google-generativeai' package is not installed."
        if GEMINI_IMPORT_ERROR:
            msg += f" Debug info: {GEMINI_IMPORT_ERROR}"
        return False, {"message": msg}
    
    # Re-check API key in case it was loaded late
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, {"message": "No Gemini API key configured."}

    if not GEMINI_API_KEY: # Ensure configured if module-level failed
        genai.configure(api_key=api_key)

    # Try multiple models in case the preferred one is unavailable or 404s
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]
    errors = []

    for model_name in models_to_try:
        try:
            logger.info(f"Sending request to Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Enforce JSON output only for 1.5 models which support it natively
            if "1.5" in model_name:
                generation_config = genai.GenerationConfig(response_mime_type="application/json")
            else:
                generation_config = None

            response = model.generate_content(prompt, generation_config=generation_config)
            
            return True, parse_json_response(response.text)

        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            errors.append(f"{model_name}: {e}")
            continue

    # Fallback: Dynamically discover available models if hardcoded ones failed
    try:
        logger.info("Hardcoded models failed. Attempting to discover available models via ListModels.")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name
                # Check if we already tried this model (ignoring 'models/' prefix)
                stripped_name = name.replace('models/', '')
                if stripped_name in models_to_try:
                    continue
                
                # We prefer Gemini models
                if 'gemini' not in name.lower():
                    continue

                try:
                    logger.info(f"Sending request to discovered model: {name}")
                    model = genai.GenerativeModel(name)
                    
                    if "1.5" in name:
                        generation_config = genai.GenerationConfig(response_mime_type="application/json")
                    else:
                        generation_config = None

                    response = model.generate_content(prompt, generation_config=generation_config)
                    
                    return True, parse_json_response(response.text)
                except Exception as e:
                    logger.warning(f"Discovered model {name} failed: {e}")
                    errors.append(f"{name}: {e}")
                    continue
    except Exception as e:
        logger.warning(f"Failed to list models: {e}")
        errors.append(f"ListModels: {e}")

    error_msg = " | ".join(errors)
    logger.error(f"All AI models failed. Errors: {error_msg}")
    return False, {"message": f"All models failed: {error_msg}"}


def generate_openai_compatible_analysis(prompt):
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", os.getenv("AI_MODEL", "gpt-4o-mini"))

    if not api_key:
        return False, {"message": "No OpenAI-compatible API key configured."}

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Return only valid JSON that matches the requested schema.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        return True, parse_json_response(content)
    except Exception as exc:
        logger.exception("OpenAI-compatible provider failed: %s", exc)
        return False, {"message": f"OpenAI-compatible provider failed: {exc}"}


def generate_ai_analysis(prompt):
    """
    Generates AI analysis using the configured provider.

    AI_PROVIDER values:
    - gemini: Google Gemini, default.
    - openai: Any OpenAI-compatible chat completions endpoint.
    - local: Alias for OpenAI-compatible local endpoints via OPENAI_BASE_URL.
    """
    provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()

    if provider == "gemini":
        return generate_gemini_analysis(prompt)
    if provider in ("openai", "openai_compatible", "local"):
        return generate_openai_compatible_analysis(prompt)

    return False, {"message": f"Unsupported AI_PROVIDER '{provider}'."}
