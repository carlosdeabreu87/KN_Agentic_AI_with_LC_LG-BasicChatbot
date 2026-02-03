"""
Scan local Ollama API for available models.
Returns list of model names or None on failure (caller falls back to config).
"""
import json
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 2


def fetch_ollama_models(base_url: str = "http://localhost:11434") -> list[str] | None:
    """
    GET /api/tags from Ollama. Response: {"models": [{"name": "..."}, ...]}.
    Returns list of model names or None on failure.
    """
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None
    models = data.get("models")
    if not models or not isinstance(models, list):
        return None
    names = []
    for m in models:
        if isinstance(m, dict) and m.get("name"):
            names.append(m["name"])
    return names if names else None
