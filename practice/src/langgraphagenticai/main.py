import streamlit as st

from src.langgraphagenticai.ui.streamlit.loadui import LoadStreamlitUI
from src.langgraphagenticai.ui.streamlit.display_result import DisplayResultStreamlit
from src.langgraphagenticai.LLMS.llm_factory import get_llm
from src.langgraphagenticai.graph.graph_builder import GraphBuilder


def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    """
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    if "messages" in st.session_state:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_message = st.chat_input("Enter your message:")

    if user_message:
        try:
            model = get_llm(user_input)
            if not model:
                st.error("Error: LLM model could not be initialized.")
                return

            usecase = user_input.get("selected_usecase")
            if not usecase:
                st.error("Error: No use case selected.")
                return

            graph_builder = GraphBuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase)
                DisplayResultStreamlit(
                    usecase, graph, user_message
                ).display_result_on_ui()
            except Exception as e:
                st.error(f"Error: Graph set up failed - {e}")
                return
        except Exception as e:
            st.error(f"Error: {e}")
            return
