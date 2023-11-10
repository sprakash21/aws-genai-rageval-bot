import os
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings, BedrockEmbeddings
from src.config.bedrock_client import get_bedrock_client
load_dotenv()


def get_db_type():
    db_local = False
    is_db_local = os.environ.get("IS_DB_LOCAL")
    if is_db_local == "true":
        db_local = True
    return db_local

def get_embedding_model(use_bedrock):
    if use_bedrock:
        # Invoke Bedrock titan embeddings
        bedrock_client = get_bedrock_client(region=os.environ.get("BEDROCK_REGION", "eu-central-1"))
        embedding = BedrockEmbeddings(client=bedrock_client, model_id="amazon.titan-embed-text-v1")
    else:
        embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
        )
    return embedding
