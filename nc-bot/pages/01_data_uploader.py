import streamlit as st
from helpers.file_upload_helper import FileUpload

st.sidebar.markdown("# Data Uploader")
st.title("Data Uploader")
st.caption("Extend the Vector Database by uploading Pdf data")

uploaded_files = st.file_uploader("Choose a PDF File", accept_multiple_files=True, type=["pdf"])
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)
    st.write(bytes_data)