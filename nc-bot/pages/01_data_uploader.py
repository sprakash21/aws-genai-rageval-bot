# import os
from rag_application_framework.modules.file_uploader.file_system_file_uploader import (
    FileSystemFilesUploader,
)
import streamlit as st

# from rag_application_framework.config.app_config import get_db_type
# from rag_application_framework import S3FileUpload
# from rag_application_framework.helpers.upload_vectordb_helper import UploadHelper
# from dotenv import load_dotenv
# import boto3

# load_dotenv()

from rag_application_framework.db.psycopg_connection_factory import (
    PsycopgConnectionFactory,
)
from rag_application_framework.config.app_config_factory import AppConfigFactory
from rag_application_framework.db.embeddings_database import EmbeddingsDatabase
from rag_application_framework.modules.file_uploader.s3_file_uploader import (
    S3FilesUploader,
)
from rag_application_framework.aws.aws_session_factory import AwsSessionFactory

app_config = AppConfigFactory.build_from_env()
db_connection_factory = PsycopgConnectionFactory(
    host=app_config.db_config.host,
    port=app_config.db_config.port,
    username=app_config.db_config.user,
    password=app_config.db_config.password,
    database_name=app_config.db_config.database,
)

embeddings_db = EmbeddingsDatabase(
    vector_db=db_connection_factory,
    collection_name=app_config.embedding_config.collection_name,
    embeddings=app_config.embedding_config.embeddings,
)


if app_config.file_store_config.is_s3:
    boto3_session = AwsSessionFactory.create_session_from_config(app_config.aws_config)
    file_uploader = S3FilesUploader(
        embeddings=app_config.embedding_config.embeddings,
        embeddings_database=embeddings_db,
        bucket_name=str(app_config.file_store_config.storage_bucket_name),
        boto3_session=boto3_session,
    )
else:
    file_uploader = FileSystemFilesUploader(
        embeddings=app_config.embedding_config.embeddings,
        embeddings_database=embeddings_db,
        folder_path=str(app_config.file_store_config.storage_path),
    )


def clear_db_show_toast():
    file_uploader.clear_context_db()
    st.toast(
        "Database is cleared successfully.",
    )


st.sidebar.markdown("# Data Uploader")
st.title("Data Uploader")
st.caption("Extend the Vector Database by uploading Pdf data")
btn = st.button("Refresh Database", on_click=clear_db_show_toast)


uploaded_files = st.file_uploader(
    "Choose a PDF File", accept_multiple_files=True, type=["pdf"]
)

for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    fname = uploaded_file.name.replace(" ", "-")
    presigned_source_url = file_uploader.upload_and_get_url(
        file_content=bytes_data,
        file_name=f"{fname}",
    )
    st.write(f"{uploaded_file.name} is uploaded successfully to S3")
    st.write(
        f"You can access it from - <a href='{presigned_source_url}'>{fname}</a>",
        unsafe_allow_html=True,
    )
