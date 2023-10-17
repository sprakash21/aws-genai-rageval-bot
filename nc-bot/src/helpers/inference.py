from langchain import hub
import os
import psycopg2
from typing import Dict
import json
from dotenv import load_dotenv
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
# LLM
from langchain.llms.ollama import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from src.helpers.upload_vectordb import get_connection_str

load_dotenv()


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({prompt: prompt, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


def create_prompt_template():
    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Use three sentences maximum and keep the answer as concise as possible. 
    Always say "thanks for asking!" at the end of the answer and if asked for your name answer as swara. 
    {context}
    Question: {question}
    Helpful Answer:"""
    rag_prompt_custom = PromptTemplate.from_template(template)
    return rag_prompt_custom


def inference(query, local=False):
    COLLECTION_NAME = "time_reporting"
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=get_connection_str(),
        embedding_function=embedding,
    )
    content_handler = ContentHandler()
    if local:
        # Local llm llama
        llm = Ollama(model="llama2",
             verbose=True,
             temperature=0.8,
             top_k=10,
             top_p=0.9,
             repeat_penalty=1.3,
             repeat_last_n=0,
             stop=["</s>"])
             #callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    else:
        llm = SagemakerEndpoint(
            endpoint_name="endpoint-name",
            credentials_profile_name="credentials-profile-name",
            region_name="us-west-2",
            model_kwargs={"temperature": 1e-10},
            content_handler=content_handler,
        )
    # Rag pipeline
    # rag_prompt = hub.pull("rlm/rag-prompt")
    rag_prompt = hub.pull("rlm/rag-prompt-llama")
    retriever = vector_store.as_retriever()
    print(rag_prompt)
    #prompt_template = create_prompt_template()
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
    )
    response = rag_chain.invoke(query)
    return response
