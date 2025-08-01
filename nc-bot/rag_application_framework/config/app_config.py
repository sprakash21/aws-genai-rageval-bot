from dataclasses import dataclass
from typing import Optional, Union, Literal
from rag_application_framework.config.app_enums import InferenceEngine
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from botocore.client import BaseClient
from datetime import datetime

@dataclass
class DbConfig:
    database: str
    user: str
    password: str
    port: int
    host: str


@dataclass
class EmbeddingConfig:
    collection_name: str
    embeddings: Union[BedrockEmbeddings, HuggingFaceEmbeddings]
    use_bedrock: bool
    bedrock_region: Optional[str] = None
    bedrock_profile: Optional[str] = None


@dataclass
class OpenAIConfig:
    api_key: str
    api_type: str
    api_version: str
    api_base: str
    deployment_name: str


@dataclass
class AwsConfig:
    region_name: Optional[str]
    profile_name: Optional[str]


@dataclass
class InferenceConfig:
    inference_engine: InferenceEngine
    sagemaker_endpoint: Optional[str] = None
    bedrock_client: Optional[BaseClient] = None
    bedrock_model_id: Optional[str] = None


@dataclass
class EvaluationConfig:
    evaluation_engine: str = "bedrock"
    bedrock_client: Optional[BaseClient] = None
    bedrock_model_id: Optional[str] = None


@dataclass
class FileStoreConfig:
    is_s3: bool = True
    storage_bucket_name: Optional[str] = None
    storage_path: Optional[str] = None


@dataclass
class ConfluenceConfig:
    url: str
    api_key: str
    username: str


@dataclass
class CognitoConfig:
    client_id: str
    client_secret: str
    username: str = None
    password: str = None


@dataclass
class SessionToken:
    access_token: str
    refresh_token: str
    granted_time: datetime = datetime.utcnow()
    expiry_time: int = 3600


@dataclass
class AppConfig:
    db_config: DbConfig
    embedding_config: EmbeddingConfig
    aws_config: AwsConfig
    inference_config: InferenceConfig
    file_store_config: FileStoreConfig
    cognito_config: Optional[CognitoConfig] = None
    openai_config: Optional[OpenAIConfig] = None
    evaluation_config: Optional[EvaluationConfig] = None
    confluence_config: Optional[ConfluenceConfig] = None
