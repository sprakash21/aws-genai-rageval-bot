import re
import boto3
from typing import Union
from botocore.client import BaseClient
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from rag_application_framework.aws.bedrock_api import BedrockApi


class LangchainEmbeddingsFactory:
    @staticmethod
    def get_bedrock_embeddings(
        bedrock_client: BaseClient,
    ) -> BedrockEmbeddings:
        # Invoke Bedrock titan embeddings
        return BedrockEmbeddings(
            client=bedrock_client, model_id="amazon.titan-embed-text-v1"
        )

    @staticmethod
    def get_huggingface_embeddings() -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    @staticmethod
    def get_embeddings(
        use_bedrock: bool,
        bedrock_api: Union[BedrockApi, None] = None,
    ) -> Union[BedrockEmbeddings, HuggingFaceEmbeddings]:
        if use_bedrock:
            assert bedrock_api is not None
            return LangchainEmbeddingsFactory.get_bedrock_embeddings(
                bedrock_client=bedrock_api.client
            )
        else:
            return LangchainEmbeddingsFactory.get_huggingface_embeddings()
