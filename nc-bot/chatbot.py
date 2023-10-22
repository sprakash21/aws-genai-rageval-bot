import streamlit as st
from src.helpers.inference import inference

st.sidebar.markdown("# Chatbot 💬")
st.title("Chatbot 💬")
st.caption("🚀 Swara - A chatbot which is works on answering pdf data")
st.markdown("## WIP")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me some Question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# New response generation
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # TODO: Should make a call to lambda
            response = inference(prompt, local=False)
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
