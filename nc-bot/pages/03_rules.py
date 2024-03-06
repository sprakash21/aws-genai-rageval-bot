import streamlit as st
import os


def page():
    st.markdown("# Rules for the Chatbot 💬")


empty = st.empty()
if "login" not in st.session_state:
    t_code = empty.text_input("Passcode", key="passcode")
    if t_code == os.environ["LOGIN_CODE"]:
        empty.empty()
        st.session_state["login"] = True
        page()
else:
    empty.empty()
    page()
