import streamlit as st

from src.langgraphagenticai.ui.streamlit.uiconfigfile import Config
from src.langgraphagenticai.LLMS.local_model_scanner import fetch_ollama_models, pull_ollama_model
from src.langgraphagenticai.LLMS.groq_models import fetch_groq_models


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def _get_model_options_for_local_provider(self, provider: str):
        if "scanned_local_models" not in st.session_state:
            st.session_state.scanned_local_models = {}
        cached = st.session_state.scanned_local_models.get(provider)
        if cached is not None and len(cached) > 0:
            return cached, None
        if provider == "Ollama":
            models, error = fetch_ollama_models()
            if error:
                return self.config.get_model_options_for_provider(provider), error
            if models:
                st.session_state.scanned_local_models[provider] = models
                return models, None
            return [], None
        return self.config.get_model_options_for_provider(provider), None

    def load_streamlit_ui(self):
        st.set_page_config(
            page_title="🤖 " + self.config.get_page_title(),
            layout="wide",
        )
        st.header("🤖 " + self.config.get_page_title())

        with st.sidebar:
            provider_options = self.config.get_provider_options()
            self.user_controls["selected_provider"] = st.selectbox(
                "Select provider",
                provider_options,
            )
            selected_provider = self.user_controls["selected_provider"]

            # Groq: API key first, then fetch models, family, model, text area
            if selected_provider == "Groq":
                api_key_label = "Groq API Key"
                self.user_controls["api_key"] = st.text_input(
                    api_key_label,
                    type="password",
                )
                if st.button("Fetch Groq models"):
                    if not self.user_controls["api_key"]:
                        st.warning("Enter your Groq API key first.")
                    else:
                        with st.spinner("Fetching models..."):
                            by_family, error = fetch_groq_models(
                                self.user_controls["api_key"]
                            )
                            if by_family:
                                st.session_state.groq_models_by_family = (
                                    by_family
                                )
                                st.success("Models loaded.")
                                st.rerun()
                            else:
                                st.error(f"Could not fetch models: {error}")

                if "groq_models_by_family" in st.session_state:
                    by_family = st.session_state.groq_models_by_family
                    families = sorted(by_family.keys())
                    self.user_controls["selected_family"] = st.selectbox(
                        "Model family",
                        families,
                        key="groq_family",
                    )
                    family = self.user_controls["selected_family"]
                    model_options = by_family.get(family, [])
                    self.user_controls["selected_model"] = st.selectbox(
                        "Select model",
                        model_options,
                        key="groq_model",
                    )
                    st.text_area(
                        "Available models (family)",
                        value="\n".join(model_options),
                        height=120,
                        disabled=True,
                    )
                else:
                    self.user_controls["selected_family"] = None
                    self.user_controls["selected_model"] = st.selectbox(
                        "Select model",
                        self.config.get_model_options_for_provider("Groq"),
                        key="groq_model_fallback",
                    )
                    st.caption(
                        "Enter API key and click 'Fetch Groq models' to see all models by family."
                    )
                if not self.user_controls["api_key"]:
                    st.warning("Please enter your Groq API key to proceed.")

            # OpenAI: family then model then API key
            elif selected_provider == "OpenAI":
                families = self.config.get_model_families_for_provider(
                    "OpenAI"
                )
                self.user_controls["selected_family"] = (
                    st.selectbox(
                        "Model family",
                        families,
                        key="openai_family",
                    )
                    if families
                    else None
                )
                family = self.user_controls["selected_family"] or (
                    families[0] if families else "ChatGPT"
                )
                model_options = self.config.get_models_for_provider_family(
                    "OpenAI", family
                )
                self.user_controls["selected_model"] = st.selectbox(
                    "Select model",
                    model_options,
                    key="openai_model",
                )
                api_key_label = "OpenAI API Key"
                self.user_controls["api_key"] = st.text_input(
                    api_key_label,
                    type="password",
                )
                if not self.user_controls["api_key"]:
                    st.warning("Please enter your OpenAI API key to proceed.")

            # Ollama: show installed and available models with install option
            elif self.config.is_local_provider(selected_provider):
                self.user_controls["api_key"] = ""
                self.user_controls["selected_family"] = None

                # Get installed models
                installed_models, error = self._get_model_options_for_local_provider(selected_provider)
                if error:
                    st.warning(f"Ollama: {error}")
                    installed_models = []

                # Refresh button
                if st.button("Refresh installed models"):
                    st.session_state.scanned_local_models.pop(selected_provider, None)
                    st.rerun()

                # Model selection (only installed models can be used)
                if installed_models:
                    self.user_controls["selected_model"] = st.selectbox(
                        "Select model",
                        installed_models,
                        key="ollama_model",
                    )
                else:
                    self.user_controls["selected_model"] = None
                    st.warning("No models installed. Install a model below.")

                st.info("No API key needed for local providers.")

                # Available models section
                st.divider()
                st.subheader("Available Models")

                available_models = self.config.get_ollama_available_models()
                installed_set = set(installed_models) if installed_models else set()

                for model in available_models:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if model in installed_set:
                            st.write(f"✅ {model}")
                        else:
                            st.write(f"⬜ {model}")
                    with col2:
                        if model not in installed_set:
                            if st.button("Install", key=f"install_{model}"):
                                with st.spinner(f"Installing {model}... This may take a while."):
                                    success, message = pull_ollama_model(model)
                                    if success:
                                        st.success(message)
                                        st.session_state.scanned_local_models.pop(selected_provider, None)
                                        st.rerun()
                                    else:
                                        st.error(message)

            else:
                self.user_controls["selected_family"] = None
                model_options = self.config.get_model_options_for_provider(
                    selected_provider
                )
                self.user_controls["selected_model"] = st.selectbox(
                    "Select model",
                    model_options,
                )
                api_key_label = (
                    f"{selected_provider} API Key"
                )
                self.user_controls["api_key"] = st.text_input(
                    api_key_label,
                    type="password",
                )
                if not self.user_controls["api_key"]:
                    st.warning("Please enter your API key to proceed.")

            usecase_options = self.config.get_usecase_options()
            self.user_controls["selected_usecase"] = st.selectbox(
                "Select use case",
                usecase_options,
            )

            st.divider()
            if st.button("Clear Chat", type="secondary"):
                st.session_state.messages = []
                st.rerun()

        return self.user_controls
