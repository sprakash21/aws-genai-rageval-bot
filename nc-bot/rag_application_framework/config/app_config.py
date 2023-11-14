from dataclasses import dataclass
from typing import Optional, Union

from langchain.embeddings import BedrockEmbeddings, HuggingFaceEmbeddings


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
    local: bool
    sagemaker_endpoint: Optional[str] = None


@dataclass
class FileStoreConfig:
    is_s3: bool = True
    storage_bucket_name: Optional[str] = None
    storage_path: Optional[str] = None


@dataclass
class AppConfig:
    db_config: DbConfig
    embedding_config: EmbeddingConfig
    openai_config: OpenAIConfig
    aws_config: AwsConfig
    inference_config: InferenceConfig
    file_store_config: FileStoreConfig
