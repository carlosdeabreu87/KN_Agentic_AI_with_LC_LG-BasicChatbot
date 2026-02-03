import streamlit as st

from src.langgraphagenticai.ui.streamlit.uiconfigfile import Config
from src.langgraphagenticai.LLMS.local_model_scanner import fetch_ollama_models


class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def _get_model_options_for_local_provider(self, provider: str):
        if "scanned_local_models" not in st.session_state:
            st.session_state.scanned_local_models = {}
        cached = st.session_state.scanned_local_models.get(provider)
        if cached is not None and len(cached) > 0:
            return cached, False
        if provider == "Ollama":
            models = fetch_ollama_models()
        else:
            return self.config.get_model_options_for_provider(provider), False
        if models:
            st.session_state.scanned_local_models[provider] = models
            return models, False
        fallback = self.config.get_model_options_for_provider(provider)
        return fallback, True

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
            if self.config.is_local_provider(selected_provider):
                model_options, used_fallback = (
                    self._get_model_options_for_local_provider(selected_provider)
                )
                if used_fallback:
                    st.caption(
                        f"Could not reach {selected_provider}; using config list."
                    )
                if "scanned_local_models" in st.session_state and st.button(
                    "Refresh models"
                ):
                    st.session_state.scanned_local_models.pop(
                        selected_provider, None
                    )
                    st.rerun()
            else:
                model_options = self.config.get_model_options_for_provider(
                    selected_provider
                )

            self.user_controls["selected_model"] = st.selectbox(
                "Select model",
                model_options,
            )

            if self.config.is_local_provider(
                self.user_controls["selected_provider"]
            ):
                self.user_controls["api_key"] = ""
                st.info("No API key needed for local providers.")
            else:
                api_key_label = (
                    f"{self.user_controls['selected_provider']} API Key"
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

        return self.user_controls
