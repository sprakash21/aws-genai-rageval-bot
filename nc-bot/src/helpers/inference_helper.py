import os
import asyncio
from langchain import hub
from dotenv import load_dotenv
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain.schema.runnable import RunnablePassthrough
from src.handlers.db_callback_handler import DBCallbackHandler 
import langchain
from langchain.retrievers import BM25Retriever, EnsembleRetriever

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
            temperature=0.9,
            top_k=50,
            top_p=0.6,
            repeat_penalty=1.3,
            repeat_last_n=0,
            stop=["</s>"],
            # callbacks=[DBCallbackHandler()]
        )
        # Explore k
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 5, 'fetch_k': 20})
        #retriever = vector_store.as_retriever()
        # RetrievalQA
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True,
            input_key="question",
            return_source_documents=True
        )
        result = qa_chain(
            {"question": query},callbacks=[DBCallbackHandler()]
        )
        print(result.keys())
        print(result["source_documents"])
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
                "temperature": 0.5,
                "top_k": 30,
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

