import streamlit as st


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.session_state.messages.append({"role": "user", "content": self.user_message})

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if self.usecase == "Basic Chatbot":
            assistant_content = None
            for event in self.graph.stream({"messages": ("user", self.user_message)}):
                for value in event.values():
                    if "messages" in value and value["messages"]:
                        assistant_content = value["messages"].content
            if assistant_content is not None:
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_content}
                )
                with st.chat_message("assistant"):
                    st.write(assistant_content)
        else:
            with st.chat_message("assistant"):
                st.write("This use case is not yet implemented.")
            st.session_state.messages.append(
                {"role": "assistant", "content": "This use case is not yet implemented."}
            )
