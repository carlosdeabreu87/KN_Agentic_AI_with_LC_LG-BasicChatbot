from configparser import ConfigParser
from pathlib import Path


class Config:
    def __init__(self, config_file=None):
        self.config = ConfigParser()
        if config_file is None:
            config_file = Path(__file__).parent / "uiconfigfile.ini"
        self.config.read(config_file)

    def get_provider_options(self):
        return self.config["DEFAULT"].get("PROVIDER_OPTIONS").split(", ")

    def get_llm_options(self):
        return self.config["DEFAULT"].get("LLM_OPTIONS").split(", ")

    def get_groq_model_options(self):
        return self.config["DEFAULT"].get("GROQ_MODEL_OPTIONS").split(", ")

    def get_openai_model_options(self):
        return self.config["DEFAULT"].get("OPENAI_MODEL_OPTIONS").split(", ")

    def get_local_providers(self):
        return self.config["DEFAULT"].get("LOCAL_PROVIDERS").split(", ")

    def is_local_provider(self, provider: str) -> bool:
        return provider in self.get_local_providers()

    def get_ollama_model_options(self):
        return self.config["DEFAULT"].get("OLLAMA_MODEL_OPTIONS").split(", ")

    def get_model_options_for_provider(self, provider: str):
        if provider == "OpenAI":
            return self.get_openai_model_options()
        if provider == "Groq":
            return self.get_groq_model_options()
        if provider == "Ollama":
            return self.get_ollama_model_options()
        return []

    def get_usecase_options(self):
        return self.config["DEFAULT"].get("USECASE_OPTIONS").split(", ")

    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE")