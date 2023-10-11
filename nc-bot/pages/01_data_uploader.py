import os
import streamlit as st
from src.helpers.file_upload_helper import S3FileUpload
from dotenv import load_dotenv

load_dotenv()

st.sidebar.markdown("# Data Uploader")
st.title("Data Uploader")
st.caption("Extend the Vector Database by uploading Pdf data")

uploaded_files = st.file_uploader("Choose a PDF File", accept_multiple_files=True, type=["pdf"])
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    s3_client = S3FileUpload()
    fname = uploaded_file.name.replace(" ", "-")
    status = s3_client.put_object(bytes_data, fname)
    if status:
        st.write(f"{uploaded_file.name} is uploaded successfully to S3")
        bucket_name = os.environ.get("BUCKET_NAME")
        s3_uri = f"https://{bucket_name}.s3.eu-central-1.amazonaws.com/{fname}"
        st.write(f"You can access it from - {s3_uri}")
