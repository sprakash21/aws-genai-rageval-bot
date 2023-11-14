import os
from typing import List, Optional
from langchain import hub
from langchain.chains import RetrievalQA
from langchain.llms.ollama import Ollama
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain.vectorstores.pgvector import PGVector
from numpy import source
from sympy import O
from rag_application_framework.aws.sagemaker_runtime_api import SagemakerRuntimeApi
from rag_application_framework.config.app_config import (
    EmbeddingConfig,
    InferenceConfig,
    OpenAIConfig,
)
from rag_application_framework.db.psycopg_connection_factory import (
    PsycopgConnectionFactory,
)
from rag_application_framework.handlers.ragas_evaluation_and_db_logging_callback_handler import (
    RagasEvaluationAndDbLoggingCallbackHandler,
)
from rag_application_framework.handlers.content_transformation_handler import (
    ContentTransformationHandler,
)
from rag_application_framework.logging.logging import Logging
from sqlalchemy.engine import Engine
from langchain.schema import Document
from rag_application_framework.aws.s3_api import S3Api
from rag_application_framework.config.app_config import FileStoreConfig
from dataclasses import dataclass

logger = Logging.get_logger(__name__)


@dataclass
class SourceDocument:
    url: str
    display_key: str


class BotRagPipeline:
    # Generate a docstring for the class
    """
    A class to perform inference using the Llama2 LLM.
    """

    def __init__(
        self,
        openai_config: OpenAIConfig,
        embeddings_config: EmbeddingConfig,
        engine: Engine,
        inference_config: InferenceConfig,
        file_store_config: FileStoreConfig,
        db_factory: PsycopgConnectionFactory,
        sagemaker_runtime_api: Optional[SagemakerRuntimeApi] = None,
        s3_api: Optional[S3Api] = None,
    ) -> None:
        if not inference_config.local and not sagemaker_runtime_api:
            raise ValueError(
                "SagemakerRuntimeApi must be provided when running in local mode"
            )

        self.openai_config = openai_config
        self.embeddings_config = embeddings_config
        self.engine = engine
        self.inference_config = inference_config
        self.db_factory = db_factory
        self.prompt = hub.pull("rlm/rag-prompt-llama")
        self.sagemaker_runtime_api = sagemaker_runtime_api
        self.s3_api = s3_api
        self.file_store_config = file_store_config

    def infer(self, query):
        """
        Perform inference using the Llama2 LLM locally using the query and the vectordb
        """
        if self.inference_config.local:
            result = self._inference_local(query)
        else:
            result = self._inference_with_sagemaker_endpoint(query)
        if self.file_store_config.is_s3:
            result["source_documents"] = self._prepare_source_documents_s3(
                result["source_documents"]
            )
        else:
            result["source_documents"] = self._prepare_source_documents_local(
                result["source_documents"]
            )
        return result

    def _inference_local(self, query):
        """
        Perform inference using the Llama2 LLM locally using the query and the vectordb
        """

        vector_store = PGVector(
            collection_name=self.embeddings_config.collection_name,
            connection_string=self.db_factory.get_connection_str(),
            embedding_function=self.embeddings_config.embeddings,
        )

        ragas_scoring_callback_handler = RagasEvaluationAndDbLoggingCallbackHandler(
            openai_config=self.openai_config,
            embeddings_config=self.embeddings_config,
            engine=self.engine,
        )

        rag_prompt = self.prompt
        print("Rag--", rag_prompt)
        # Local llm llama
        llm = Ollama(
            model="llama2",
            verbose=True,
            temperature=0.9,
            top_k=50,
            top_p=0.6,
            repeat_penalty=1.3,
            repeat_last_n=0,
            stop=["</s>"],
            mirostat=None,
            mirostat_eta=None,
            mirostat_tau=None,
            num_ctx=None,
            num_gpu=None,
            num_thread=None,
            tfs_z=None,
        )
        # Explore k
        retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20}
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True,
            input_key="question",
            return_source_documents=True,
        )

        result = qa_chain(
            {"question": query}, callbacks=[ragas_scoring_callback_handler]
        )
        logger.info(result.keys())
        logger.info(result["source_documents"])
        return result

    def _inference_with_sagemaker_endpoint(self, query):
        """
        Perform inference using the Llama2 LLM through AWS via Sagemaker Endpoint and the vectordb
        """
        if not self.sagemaker_runtime_api:
            raise ValueError("Sagemaker Api must be present.")

        ragas_scoring_callback_handler = RagasEvaluationAndDbLoggingCallbackHandler(
            openai_config=self.openai_config,
            embeddings_config=self.embeddings_config,
            engine=self.engine,
        )
        vector_store = PGVector(
            collection_name=self.embeddings_config.collection_name,
            connection_string=self.db_factory.get_connection_str(),
            embedding_function=self.embeddings_config.embeddings,
        )
        rag_prompt = self.prompt

        content_handler = ContentTransformationHandler()

        llm = SagemakerEndpoint(
            endpoint_name=str(self.inference_config.sagemaker_endpoint),
            model_kwargs={
                "do_sample": True,
                "temperature": 0.5,
                "top_k": 30,
                "top_p": 0.9,
                "repetition_penalty": 1.3,
                "repeat_last_n": 0,
                "max_new_tokens": 512,
                "stop": ["</s>"],
                "return_full_text": False,
            },
            content_handler=content_handler,
            client=self.sagemaker_runtime_api.client,
        )

        retriever = vector_store.as_retriever(k=3)
        # RetrievalQA
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True,
            return_source_documents=True,
            input_key="question",
        )
        result = qa_chain(
            {"question": query},
            callbacks=[ragas_scoring_callback_handler],
        )
        print("Results-----", result.keys())
        return result

    def _prepare_source_documents_s3(
        self, source_docs: List[Document]
    ) -> list[SourceDocument]:
        source_doc_uris: List[SourceDocument] = []

        if not self.s3_api:
            raise ValueError("S3Api must be present.")

        for doc in source_docs:
            if hasattr(doc, "metadata"):
                source_uri = doc.metadata["source"]
                bucket_name = source_uri.split("/")[2]
                full_file_key = "/".join(source_uri.split("/")[3:])
                url = self.s3_api.generate_presigned_url(
                    bucket_name=bucket_name,
                    fname=full_file_key,
                )

                source_doc_uris.append(
                    SourceDocument(
                        url=url,
                        display_key=source_uri,
                    )
                )
        return source_doc_uris

    def _prepare_source_documents_local(
        self, source_docs: List[Document]
    ) -> list[SourceDocument]:
        source_doc_uris: List[SourceDocument] = []
        for doc in source_docs:
            if hasattr(doc, "metadata"):
                source_uri = doc.metadata["source"]
                absolute_path = source_uri
                url = f"file://{absolute_path}"
                display_key = source_uri
                source_doc_uris.append(
                    SourceDocument(
                        url=url,
                        display_key=display_key,
                    )
                )
        return source_doc_uris
