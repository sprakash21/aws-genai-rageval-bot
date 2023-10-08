import streamlit as st

st.sidebar.markdown("# Chatbot 💬")
st.title("Chatbot 💬")
st.caption("🚀 Swara - A chatbot which is works on answering pdf data")
st.markdown("## WIP")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me some Question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = f"Echo: {prompt}"
    # Display swara response in chat message container
    with st.chat_message("swara"):
        st.markdown(response)
    # Add swara response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
