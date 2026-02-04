"""
Scan local Ollama API for available models and pull new models.
"""
import requests

DEFAULT_TIMEOUT = 5
PULL_TIMEOUT = 600  # 10 minutes for model download


def fetch_ollama_models(base_url: str = "http://localhost:11434") -> tuple[list[str] | None, str | None]:
    """
    GET /api/tags from Ollama. Response: {"models": [{"name": "..."}, ...]}.
    Returns tuple of (list of model names, error_message).
    On success: (names, None)
    On failure: (None, error_message)
    """
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to Ollama. Is it running?"
    except requests.exceptions.RequestException as e:
        return None, str(e)

    models = data.get("models")
    if not models or not isinstance(models, list):
        return [], None  # No models installed yet

    names = []
    for m in models:
        if isinstance(m, dict) and m.get("name"):
            # Strip the tag suffix for cleaner display (e.g., "llama3.2:latest" -> "llama3.2")
            name = m["name"]
            if ":" in name:
                name = name.split(":")[0]
            if name not in names:
                names.append(name)
    return names if names else [], None


def pull_ollama_model(model_name: str, base_url: str = "http://localhost:11434") -> tuple[bool, str]:
    """
    POST to /api/pull to download a model.
    Returns tuple of (success, message).
    """
    url = f"{base_url.rstrip('/')}/api/pull"
    try:
        resp = requests.post(
            url,
            json={"name": model_name},
            timeout=PULL_TIMEOUT,
            stream=True,
        )
        resp.raise_for_status()

        # The response is streamed JSON lines showing progress
        last_status = ""
        for line in resp.iter_lines():
            if line:
                try:
                    data = line.decode("utf-8")
                    import json
                    status_data = json.loads(data)
                    if "status" in status_data:
                        last_status = status_data["status"]
                except:
                    pass

        return True, f"Successfully installed {model_name}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama. Is it running?"
    except requests.exceptions.Timeout:
        return False, "Download timed out. Try again or check your connection."
    except requests.exceptions.RequestException as e:
        return False, str(e)
