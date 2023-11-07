import os
from langchain import hub
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from src.handlers.db_callback_handler import DBCallbackHandler
import langchain

langchain.debug = False
# LLM
from langchain.llms.ollama import Ollama
from src.config.app_config import get_db_type
from src.handlers.content_handler import ContentHandler
from langchain.chains import RetrievalQA
from src.helpers.upload_vectordb_helper import UploadHelper
from src.helpers.env_utils import get_ssm_parameter_value


class Llama2InferenceHelper:
    # Generate a docstring for the class
    """
    A class to perform inference using the Llama2 LLM.
    """

    def __init__(self, collection_name) -> None:
        self.prompt = hub.pull("rlm/rag-prompt-llama")
        self.collection_name = collection_name
        self.sg_endpoint_name = get_ssm_parameter_value(
            os.environ.get("SG_ENDPOINT_NAME")
        )
        self.db_type = get_db_type()

    def inference_local(self, query):
        """
        Perform inference using the Llama2 LLM locally using the query and the vectordb
        """
        upload_helper = UploadHelper(db_local=self.db_type)
        collection_name = self.collection_name
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = PGVector(
            collection_name=collection_name,
            connection_string=upload_helper.get_connection_str(),
            embedding_function=embedding,
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
            # callbacks=[DBCallbackHandler()]
        )
        # Explore k
        retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20}
        )
        # retriever = vector_store.as_retriever()
        # RetrievalQA
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True,
            input_key="question",
            return_source_documents=True,
        )
        result = qa_chain({"question": query}, callbacks=[DBCallbackHandler()])
        print(result.keys())
        print(result["source_documents"])
        return result["result"]

    def inference(self, query):
        """
        Perform inference using the Llama2 LLM through AWS via Sagemaker Endpoint and the vectordb
        """
        try:
            upload_helper = UploadHelper(db_local=self.db_type)
            collection_name = self.collection_name
            embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = PGVector(
                collection_name=collection_name,
                connection_string=upload_helper.get_connection_str(),
                embedding_function=embedding,
            )
            content_handler = ContentHandler()
            rag_prompt = self.prompt
            print("Rag--", rag_prompt)
            # SagemakerEndpoint
            if self.sg_endpoint_name is None:
                raise AssertionError("Sagemaker Endpoint Name is not set")
            llm = SagemakerEndpoint(
                endpoint_name=self.sg_endpoint_name,
                region_name="os.environ.get("AWS_REGION")",
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
            result = qa_chain({"question": query}, callbacks=[DBCallbackHandler()])
            print("Results-----", result.keys())
            return result
        except Exception as e:
            print("There has been an exception with client request %s", e)
            return "There has been an error for the request..."
