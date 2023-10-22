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
from langchain.prompts import PromptTemplate, HumanMessagePromptTemplate
from langchain.schema.runnable import RunnablePassthrough
import langchain
langchain.debug = True
# LLM
from langchain.llms.ollama import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from src.helpers.upload_vectordb import get_connection_str
from langchain.chains import RetrievalQA
from langchain.callbacks import SageMakerCallbackHandler

load_dotenv()


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_dict = {"inputs": prompt, "parameters": model_kwargs}
        return json.dumps(input_dict).encode('utf-8')

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        print("output: ", response_json[0])
        return response_json[0]["generated_text"]

def build_llama2_prompt(messages):
    startPrompt = "<s>[INST] "
    endPrompt = " [/INST]"
    conversation = []
    for index, message in enumerate(messages):
        if message["role"] == "system" and index == 0:
            conversation.append(f"<<SYS>>\n{message['content']}\n<</SYS>>\n\n")
        elif message["role"] == "user":
            conversation.append(message["content"].strip())
        else:
            conversation.append(f" [/INST] {message['content'].strip()}</s><s>[INST] ")

    return startPrompt + "".join(conversation) + endPrompt

def create_prompt_template():
    template = """
    <s> [INST] 
    <<SYS>>
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use three sentences maximum and keep the answer concise. 
    If the question seems like not a question, just say you don't know the answer for the question asked. 
    <</SYS>> 
    Question: {question} 
    Context: {context} 
    Answer: [/INST]<s>
    """
    rag_prompt_custom = PromptTemplate(input_variables=['question', 'context'], template=template)
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
        llm = Ollama(
            model="llama2",
            verbose=True,
            temperature=0.8,
            top_k=10,
            top_p=0.9,
            repeat_penalty=1.3,
            repeat_last_n=0,
            return_full_text=False,
            stop=["</s>"],
        )
        # callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
        # Rag pipeline
        # rag_prompt = hub.pull("rlm/rag-prompt")
        rag_prompt = hub.pull("rlm/rag-prompt-llama")
        retriever = vector_store.as_retriever()
        # print(rag_prompt)
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | llm
        )
        response = rag_chain.invoke(query)
        print("Rag Length", len(rag_prompt))
        return response
    else:
        rag_prompt = hub.pull("rlm/rag-prompt-llama")
        print("Rag--", rag_prompt)
        llm = SagemakerEndpoint(
            endpoint_name="endpoint-meta-llama--Llama-2-13b-chat-hf",
            credentials_profile_name="nc-admin",
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

        retriever = vector_store.as_retriever(k=1)
        # RetrievalQA
        rag_prompt = hub.pull("rlm/rag-prompt-llama")
        
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": rag_prompt},
            verbose=True
        )
        result = qa_chain({"query": query},)
        print(result.keys())
        return result['result'][len(rag_prompt):]
