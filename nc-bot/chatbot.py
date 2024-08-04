import os
from typing import List
from rag_application_framework.config.app_enums import InferenceEngine
from rag_application_framework.aws.sagemaker_runtime_api import SagemakerRuntimeApi

import sqlalchemy
import streamlit as st
from rag_application_framework.aws.aws_client_factory import AwsClientFactory
from rag_application_framework.aws.aws_session_factory import AwsSessionFactory
from rag_application_framework.aws.s3_api import S3Api
from rag_application_framework.config.app_config_factory import AppConfigFactory
from rag_application_framework.db.embeddings_database import EmbeddingsDatabase
from rag_application_framework.db.models import inititalize
from rag_application_framework.db.psycopg_connection_factory import (
    PsycopgConnectionFactory,
)
from rag_application_framework.modules.chat.bot_rag_pipeline import (
    BotRagPipeline,
    SourceDocument,
)

from dotenv import load_dotenv
load_dotenv()


def page():
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

    boto3_session = None
    sagemaker_runtime_api = None
    bedrock_runtime_client = None
    s3_api = None

    if app_config.inference_config.inference_engine.name.lower() == "sagemaker":
        boto3_session = AwsSessionFactory.create_session_from_config(
            app_config.aws_config
        )
        sagemaker_runtime_api = AwsClientFactory.build_from_boto_session(
            boto3_session,
            SagemakerRuntimeApi,
        )

    if app_config.file_store_config.is_s3:
        boto3_session = AwsSessionFactory.create_session_from_config(
            app_config.aws_config
        )
        s3_api = AwsClientFactory.build_from_boto_session(
            boto3_session,
            S3Api,
        )

    engine = sqlalchemy.create_engine(
        db_connection_factory.get_connection_str(), pool_pre_ping=True
    )

    inititalize(engine)

    bot_rag_pipeline = BotRagPipeline(
        #openai_config=app_config.openai_config,
        evaluation_config = app_config.evaluation_config,
        embeddings_config=app_config.embedding_config,
        engine=engine,
        file_store_config=app_config.file_store_config,
        inference_config=app_config.inference_config,
        db_factory=db_connection_factory,
        sagemaker_runtime_api=sagemaker_runtime_api,
        s3_api=s3_api,
    )

    st.sidebar.markdown("# Chatbot 💬")
    st.title("Chatbot 💬")
    st.caption("🚀 RAGTrack - A chatbot which is works on answering on your pdf data")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask me some Question?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt, unsafe_allow_html=True)

    def prepare_source_docs(docs: List[SourceDocument]):
        mk_txt = "<details style='border:1px dotted'><summary><span style='color:DodgerBlue;'>I have been referencing\
        following documents for generation:</span>: </summary><br>"
        temp_list = list()
        for doc in docs:
            if doc.file_store_url not in temp_list:
                temp_list.append(doc.file_store_url)
                mk_txt += f'<a href="{doc.file_store_url}">{doc.display_text}</a>'

                if doc.confluence_source_info:
                    mk_txt += f' - <a href="{doc.confluence_source_info.page_url}"> Original Confluence Page </a> <br>'
                else:
                    mk_txt += f"<br>"
        mk_txt += f"</details>"
        return mk_txt

    # New response generation
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # A collection name is fixed for the application and can be extended
                response = bot_rag_pipeline.infer(prompt)

                st.write(response["result"], unsafe_allow_html=True)
                source_docs = prepare_source_docs(response["source_documents"])
                st.write(source_docs, unsafe_allow_html=True)
        message = {
            "role": "assistant",
            "content": response["result"] + "<br>" + source_docs,
        }
        st.session_state.messages.append(message)


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
