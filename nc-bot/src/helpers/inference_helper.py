import os
import asyncio
from langchain import hub
from dotenv import load_dotenv
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain.schema.runnable import RunnablePassthrough
import langchain

langchain.debug = False
# LLM
from langchain.llms.ollama import Ollama
from src.handlers.content_handler import ContentHandler
from langchain.chains import RetrievalQA
from src.helpers.upload_vectordb_helper import UploadHelper
from langchain.callbacks.base import BaseCallbackHandler
from typing import List, Dict, Any, Union
from langchain.schema.output import LLMResult
from langchain.schema.messages import BaseMessage

load_dotenv()

class MyCallBackHandler(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        print("on_llm_start Prompt --", prompts)
        print("on_llm_start Seralized --", serialized)

    # def on_chat_model_start(
    #     self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    # ) -> Any:
    #     """Run when Chat Model starts running."""
    #     print("chat_model_start messages --", messages)
    #     print("chat_model_start Seralized --", serialized)

    # def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
    #     """Run on new LLM token. Only available when streaming is enabled."""
    #     print("on_llm_new_token Seralized --", token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        print("on_llm_end Response", response)

    # def on_llm_error(
    #     self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    # ) -> Any:
    #     """Run when LLM errors."""
    #     print("on_llm_error Error--", error)

    # def on_chain_start(
    #     self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    # ) -> Any:
    #     """Run when chain starts running."""
    #     print("on_chain_start Seralized --", serialized)
    #     print("on_chain_start Inputs", inputs)

    # def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
    #     """Run when chain ends running."""
    #     print("on_chain_end Outputs", outputs)

    # def on_chain_error(
    #     self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    # ) -> Any:
    #     """Run when chain errors."""
    #     print("on_chain_error ..Chain_errors", error)

    # def on_tool_start(
    #     self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    # ) -> Any:
    #     """Run when tool starts running."""
    #     print("Tool Start ", serialized)
    #     print("Tool Start input_str", input_str)

    # def on_tool_end(self, output: str, **kwargs: Any) -> Any:
    #     """Run when tool ends running."""
    #     print("Tool End out", output)


    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        print("Tool Error", error)

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        print("Text..On", text)




class Llama2InferenceHelper:
    def __init__(self, collection_name, option="AWS") -> None:
        self.prompt = hub.pull("rlm/rag-prompt-llama")
        self.collection_name = collection_name
    
    def inference_local(self, query):
        upload_helper = UploadHelper(local=True)
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
            temperature=0.8,
            top_k=10,
            top_p=0.9,
            repeat_penalty=1.3,
            repeat_last_n=0,
            stop=["</s>"],
            callbacks=[MyCallBackHandler()]
        )
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 20})
        # RetrievalQA
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True,
            input_key="question"
        )
        result = qa_chain(
            {"question": query}
        )
        print(result.keys())
        return result["result"]

    def inference(self, query):
        upload_helper = UploadHelper()
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
        llm = SagemakerEndpoint(
            # fetch from ssm or secrets
            endpoint_name="",
            region_name="eu-central-1",
            model_kwargs={
                "do_sample": True,
                "temperature": 0.8,
                "top_k": 10,
                "top_p": 0.9,
                "repeat_penalty": 1.3,
                "repeat_last_n": 0,
                "max_new_tokens": 512,
                "stop": ["</s>"],
                "return_full_text": False
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
            input_key="question"
        )
        result = qa_chain(
            {"question": query},
        )
        print(result.keys())
        return result["result"][len(rag_prompt) :]

