"""
Fetch Groq API list of models and group by family (Llama, Mixtral, Gemma, etc.).
"""
import requests

GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
DEFAULT_TIMEOUT = 10

# Map model id prefix (lowercase) to display family name
ID_PREFIX_TO_FAMILY = {
    "llama": "Llama",
    "mixtral": "Mixtral",
    "gemma": "Gemma",
    "whisper": "Whisper",
}


def _family_from_model_id(model_id: str) -> str:
    """Derive family from model id (e.g. llama3-70b-8192 -> Llama)."""
    if not model_id:
        return "Other"
    lower = model_id.lower()
    for prefix, family in ID_PREFIX_TO_FAMILY.items():
        if lower.startswith(prefix):
            return family
    return "Other"


def fetch_groq_models(api_key: str) -> tuple[dict[str, list[str]] | None, str | None]:
    """
    GET Groq /openai/v1/models with Bearer token.
    Returns tuple of (dict mapping family name to list of model ids, error_message).
    On success: (by_family, None)
    On failure: (None, error_message)
    """
    if not api_key or not api_key.strip():
        return None, "API key is empty"
    try:
        resp = requests.get(
            GROQ_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        return None, str(e)

    items = data.get("data")
    if not items or not isinstance(items, list):
        return None, "Invalid response format from Groq API"

    by_family: dict[str, list[str]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("id"):
            mid = item["id"]
            family = _family_from_model_id(mid)
            by_family.setdefault(family, []).append(mid)
    for lst in by_family.values():
        lst.sort()

    if not by_family:
        return None, "No models found in Groq API response"

    return by_family, None
