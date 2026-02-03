from langchain_community.chat_models.ollama import ChatOllama


class OllamaLLM:
    def __init__(self, user_controls):
        self.user_controls = user_controls

    def get_llm_model(self):
        model = self.user_controls.get("selected_model", "llama3.2")
        return ChatOllama(model=model)
