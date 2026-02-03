from src.langgraphagenticai.LLMS.openaillm import OpenAILLM
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.LLMS.ollamallm import OllamaLLM


def get_llm(user_controls):
    """
    Returns the LangChain chat model for the selected provider.
    """
    provider = user_controls.get("selected_provider")
    if provider == "OpenAI":
        return OpenAILLM(user_controls).get_llm_model()
    if provider == "Groq":
        return GroqLLM(user_controls).get_llm_model()
    if provider == "Ollama":
        return OllamaLLM(user_controls).get_llm_model()
    return None
