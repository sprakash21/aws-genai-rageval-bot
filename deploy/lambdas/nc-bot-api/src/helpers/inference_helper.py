import os
from langchain import hub
from dotenv import load_dotenv
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain.schema.runnable import RunnablePassthrough
import langchain

langchain.debug = True
# LLM
from langchain.llms.ollama import Ollama
from src.handlers.content_handler import ContentHandler
from langchain.chains import RetrievalQA
from src.helpers.uploading_helper import UploadHelper

load_dotenv()


class Llama2InferenceHelper:
    def __init__(self, collection_name, endpoint) -> None:
        self.prompt = hub.pull("rlm/rag-prompt-llama")
        self.collection_name = collection_name
        self.endpoint_name = endpoint
    
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
            endpoint_name=self.endpoint_name,
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
        )
        result = qa_chain(
            {"query": query},
        )
        print(result.keys())
        return result["result"][len(rag_prompt) :]
