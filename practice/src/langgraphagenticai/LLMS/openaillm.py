import streamlit as st
from langchain_openai import ChatOpenAI


class OpenAILLM:
    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):
        try:
            api_key = self.user_controls_input["api_key"]
            model = self.user_controls_input["selected_model"]
            if not api_key:
                st.error("Please enter your OpenAI API key.")
                return None
            llm = ChatOpenAI(api_key=api_key, model=model)
        except Exception as e:
            raise ValueError(f"Error occurred with OpenAI: {e}")
        return llm
