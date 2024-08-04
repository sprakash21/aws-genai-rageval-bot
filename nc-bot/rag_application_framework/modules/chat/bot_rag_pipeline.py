from typing import List, Optional, Union
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.ollama import Ollama
from langchain_community.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.llms.bedrock import Bedrock
from rag_application_framework.aws.sagemaker_runtime_api import SagemakerRuntimeApi
from rag_application_framework.config.app_config import (
    EmbeddingConfig,
    InferenceConfig,
    EvaluationConfig
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
from langchain.prompts.chat import ChatPromptTemplate


logger = Logging.get_logger(__name__)


@dataclass
class ConfluenceSourceInfo:
    page_id: str
    page_title: str
    page_url: str


@dataclass
class SourceDocument:
    file_store_url: str
    display_text: str
    confluence_source_info: Optional[ConfluenceSourceInfo] = None


class BotRagPipeline:
    """
    A class to perform inference using the Bedrock Model LLM.
    """

    def __init__(
        self,
        embeddings_config: EmbeddingConfig,
        engine: Engine,
        inference_config: InferenceConfig,
        file_store_config: FileStoreConfig,
        db_factory: PsycopgConnectionFactory,
        #openai_config: Union[OpenAIConfig, None],
        evaluation_config: Union[EvaluationConfig, None],
        sagemaker_runtime_api: Optional[SagemakerRuntimeApi] = None,
        s3_api: Optional[S3Api] = None,
    ) -> None:
        if (
            inference_config.inference_engine.name.lower() == "sagemaker"
            and not sagemaker_runtime_api
        ):
            raise ValueError(
                "SagemakerRuntimeApi must be provided when running in local mode"
            )

        #self.openai_config = openai_config
        self.evaluation_config = evaluation_config
        self.embeddings_config = embeddings_config
        self.engine = engine
        self.inference_config = inference_config
        self.db_factory = db_factory

        template_string = (
            "[INST]<<SYS>> You are an assistant for question-answering tasks and you will only answer as much as "
            "possible by strictly looking into the context. If you don't know the answer, just say that "
            "you are trained on the uploaded document information and do not make up answers by looking into context. "
            "Use three sentences maximum and keep the answer concise. If and only if the question is about yourself, "
            "like \"who are you?\" or \"what is your name\", then ignore the given context and answer exactly "
            "with \"I am QA Bot\".<</SYS>> \n"
            "        Question: {question}\n"
            "        Context: {context} \n"
            "        Answer: \n[/INST]"
            "        ")
        self.prompt = ChatPromptTemplate.from_template(template_string)
        self.sagemaker_runtime_api = sagemaker_runtime_api
        self.s3_api = s3_api
        self.file_store_config = file_store_config

    def infer(self, query):
        """
        Perform inference using the LLM using the query and the vectordb
        """
        vector_store = PGVector(
            collection_name=self.embeddings_config.collection_name,
            connection_string=self.db_factory.get_connection_str(),
            embedding_function=self.embeddings_config.embeddings,
        )

        callback_handlers = []

        if self.evaluation_config:
            callback_handlers.append(
                RagasEvaluationAndDbLoggingCallbackHandler(
                    #openai_config=self.openai_config,
                    evaluation_config=self.evaluation_config,
                    embeddings_config=self.embeddings_config,
                    engine=self.engine,
                )
            )

        retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 30}
        )

        llm = self._get_llm()

        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": self.prompt},
            verbose=True,
            input_key="question",
            return_source_documents=True,
        )

        result = qa_chain({"question": query}, callbacks=callback_handlers)

        logger.info(f"Result: {result}")

        if self.file_store_config.is_s3:
            result["source_documents"] = self._prepare_source_documents_s3(
                result["source_documents"]
            )
        else:
            result["source_documents"] = self._prepare_source_documents_local(
                result["source_documents"]
            )
        return result

    def _get_local_llm(self) -> Ollama:
        """
        Perform inference using the LLM locally using the query and the vectordb
        """

        llm = Ollama(
            model="llama2",
            verbose=True,
            temperature=0.5,
            top_k=30,
            top_p=0.9,
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

        return llm

    def _get_llm(self) -> Union[Ollama, Bedrock, SagemakerEndpoint]:
        if self.inference_config.inference_engine.name.lower() == "local":
            llm = self._get_local_llm()
        elif self.inference_config.inference_engine.name.lower() == "sagemaker":
            llm = self._get_sagemaker_llm()
        elif self.inference_config.inference_engine.name.lower() == "bedrock":
            llm = self._get_bedrock_llm()
        else:
            raise ValueError(
                f"Invalid inference engine {self.inference_config.inference_engine.name}"
            )
        return llm

    def _get_sagemaker_llm(
        self,
    ) -> SagemakerEndpoint:
        """
        Perform inference using the LLM through AWS via Sagemaker Endpoint and the vectordb
        """
        if not self.sagemaker_runtime_api:
            raise ValueError("Sagemaker Api must be present.")

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

        return llm

    def _get_bedrock_llm(self) -> Bedrock:
        """
        Perform inference using the LLM through AWS via Bedrock and use vectordb
        """
        llm = Bedrock(
            client=self.inference_config.bedrock_client,
            model_id=str(self.inference_config.bedrock_model_id),
            model_kwargs={"temperature": 0.7, "top_p": 0.9, "max_gen_len": 512},
        )

        return llm

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
                source_doc = SourceDocument(
                    file_store_url=url,
                    display_text=source_uri,
                )
                if doc.metadata.get("confluence_id"):
                    source_doc.confluence_source_info = ConfluenceSourceInfo(
                        page_id=doc.metadata["confluence_id"],
                        page_title=doc.metadata["confluence_title"],
                        page_url=doc.metadata["confluence_source"],
                    )
                source_doc_uris.append(source_doc)
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
                source_doc = SourceDocument(
                    file_store_url=url,
                    display_text=display_key,
                )

                if doc.metadata.get("confluence_id"):
                    source_doc.confluence_source_info = ConfluenceSourceInfo(
                        page_id=doc.metadata["confluence_id"],
                        page_title=doc.metadata["confluence_title"],
                        page_url=doc.metadata["confluence_source"],
                    )

                source_doc_uris.append(source_doc)
        return source_doc_uris
