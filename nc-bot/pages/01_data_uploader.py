import os
import streamlit as st
from src.helpers.file_upload_helper import S3FileUpload
from src.helpers.upload_vectordb import process_data
from dotenv import load_dotenv

load_dotenv()

st.sidebar.markdown("# Data Uploader")
st.title("Data Uploader")
st.caption("Extend the Vector Database by uploading Pdf data")

uploaded_files = st.file_uploader(
    "Choose a PDF File", accept_multiple_files=True, type=["pdf"]
)
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    s3_client = S3FileUpload()
    fname = uploaded_file.name.replace(" ", "-")
    status = s3_client.put_object(bytes_data, "pdf_data/" + fname)
    if status:
        st.write(f"{uploaded_file.name} is uploaded successfully to S3")
        # Get the bucket_name from SSM parameters
        bucket_name = os.environ.get("BUCKET_NAME")
        s3_uri = f"https://{bucket_name}.s3.eu-central-1.amazonaws.com/pdf_data/{fname}"
        st.write(f"You can access it from - {s3_uri}")
        # TODO: Move logic to lambda for processing
        status = process_data(fname=f"pdf_data/{fname}")
        st.write(f"Status - {status}")
        # Pass this to the request for lambda
        # Lambda reads this file and puts it into vectorstore.
