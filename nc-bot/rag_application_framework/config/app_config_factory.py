import os
from typing import Optional
from botocore.config import Config
from boto3 import Session
from rag_application_framework.aws.aws_session_factory import AwsSessionFactory
from rag_application_framework.aws.aws_client_factory import AwsClientFactory
from rag_application_framework.aws.bedrock_runtime_api import BedrockRuntimeApi
from rag_application_framework.aws.secretsmanager_api import SecretsManagerApi
from rag_application_framework.aws.ssm_api import SsmApi
from rag_application_framework.config.app_enums import InferenceEngine
from rag_application_framework.config.app_config import (
    AppConfig,
    AwsConfig,
    ConfluenceConfig,
    DbConfig,
    EmbeddingConfig,
    FileStoreConfig,
    InferenceConfig,
    EvaluationConfig,
    OpenAIConfig,
)
from rag_application_framework.ml.embeddings.langchain_embeddings_factory import (
    LangchainEmbeddingsFactory,
)

from typing import Union

from rag_application_framework.logging.logging import Logging

logger = Logging.get_logger(__name__)


class AppConfigFactory:
    _boto3_session: Optional[Session] = None
    region_name = os.environ.get("AWS_REGION")
    profile_name = os.environ.get("AWS_PROFILE")
    aws_config = AwsConfig(
        region_name=region_name,
        profile_name=profile_name,
    )
    aws_session = AwsSessionFactory.create_session_from_config(aws_config)

    @staticmethod
    def build_from_env():
        #openai_config = AppConfigFactory.get_open_ai_config()
        evaluation_config = AppConfigFactory.get_evaluation_config()

        db_config = AppConfigFactory.get_db_config()

        embedding_config = AppConfigFactory.get_embedding_config()

        inference_config = AppConfigFactory.get_inference_config()

        file_store_config = AppConfigFactory.get_file_store_config()
        # No confluence configuration
        #confluence_config = AppConfigFactory.get_confluence_config()

        return AppConfig(
            db_config=db_config,
            embedding_config=embedding_config,
            #openai_config=openai_config,
            aws_config=AppConfigFactory.aws_config,
            inference_config=inference_config,
            evaluation_config=evaluation_config,
            file_store_config=file_store_config,
            #confluence_config=confluence_config,
        )

    @staticmethod
    def get_file_store_config() -> FileStoreConfig:
        bucket_name = os.environ.get("BUCKET_NAME")

        if bucket_name:
            file_store_config = FileStoreConfig(
                is_s3=True,
                storage_bucket_name=bucket_name,
            )
        else:
            file_store_config = FileStoreConfig(
                is_s3=False,
                storage_path=os.path.abspath(os.environ["LOCAL_STORAGE_PATH"]),
            )

        return file_store_config

    @staticmethod
    def get_inference_config() -> InferenceConfig:
        inference_engine = os.environ.get("INFERENCE_ENGINE", "LOCAL")
        if inference_engine.lower() == "local":
            inference_config = InferenceConfig(inference_engine=InferenceEngine.LOCAL)
        elif inference_engine.lower() == "sagemaker":
            sagemaker_endpoint = os.environ.get("SAGEMAKER_ENDPOINT")
            if not sagemaker_endpoint:
                ssm_client = AwsClientFactory.build_from_boto_session(
                    AppConfigFactory.aws_session,
                    SsmApi,
                )

                sagemaker_endpoint = ssm_client.get_parameter(
                    name=os.environ["SAGEMAKER_ENDPOINT_SSM_PARAM_NAME"],
                )

                if not sagemaker_endpoint:
                    raise ValueError("Sagemaker endpoint not specified.")

            inference_config = InferenceConfig(
                sagemaker_endpoint=sagemaker_endpoint,
                inference_engine=InferenceEngine.SAGEMAKER,
            )
        elif inference_engine.lower() == "bedrock":
            aws_config = AppConfigFactory.aws_config
            bedrock_inference_region = os.environ.get(
                "BEDROCK_INFERENCE_REGION", aws_config.region_name
            )
            bedrock_inference_profile = os.environ.get(
                "BEDROCK_INFERENCE_PROFILE", aws_config.profile_name
            )
            bedrock_model_id = os.environ["BEDROCK_INFERENCE_MODEL_ID"]
            aws_session = AwsSessionFactory.create_session_from_config(
                config=AwsConfig(
                    region_name=bedrock_inference_region,
                    profile_name=bedrock_inference_profile,
                )
            )
            bedrock_api = AwsClientFactory.build_from_boto_session(
                aws_session,
                BedrockRuntimeApi,
                client_config=Config(region_name=bedrock_inference_region),
            )
            inference_config = InferenceConfig(
                inference_engine=InferenceEngine.BEDROCK,
                bedrock_client=bedrock_api.client,
                bedrock_model_id=bedrock_model_id,
            )
        else:
            raise ValueError(f"Invalid inference engine: {inference_engine} specified")

        return inference_config
    
    @staticmethod
    def get_evaluation_config() -> EvaluationConfig:
        evaluation_engine = os.environ.get("INFERENCE_ENGINE", "bedrock")
        if evaluation_engine.lower() == "bedrock":
            aws_config = AppConfigFactory.aws_config
            bedrock_inference_region = os.environ.get(
                "BEDROCK_INFERENCE_REGION", aws_config.region_name
            )
            bedrock_inference_profile = os.environ.get(
                "BEDROCK_INFERENCE_PROFILE", aws_config.profile_name
            )
            bedrock_model_id = os.environ["BEDROCK_EVALUATION_MODEL_ID"]
            aws_session = AwsSessionFactory.create_session_from_config(
                config=AwsConfig(
                    region_name=bedrock_inference_region,
                    profile_name=bedrock_inference_profile,
                )
            )
            bedrock_api = AwsClientFactory.build_from_boto_session(
                aws_session,
                BedrockRuntimeApi,
                client_config=Config(region_name=bedrock_inference_region),
            )
            evaluation_confg = EvaluationConfig(
                evaluation_engine=evaluation_engine,
                bedrock_client=bedrock_api.client,
                bedrock_model_id=bedrock_model_id,
            )
        else:
            raise ValueError(f"Invalid inference engine: {evaluation_engine} specified")

        return evaluation_confg

    @staticmethod
    def get_embedding_config() -> EmbeddingConfig:
        use_bedrock = os.environ["USE_BEDROCK_EMBEDDINGS"].lower() == "true"
        collection_name = os.environ["EMBEDDING_COLLECTION_NAME"]

        if use_bedrock:
            aws_config = AppConfigFactory.aws_config
            bedrock_region = os.environ.get(
                "BEDROCK_EMBEDDINGS_REGION", aws_config.region_name
            )
            bedrock_profile = os.environ.get(
                "BEDROCK_EMBEDDINGS_PROFILE", aws_config.profile_name
            )
            aws_session = AwsSessionFactory.create_session_from_config(
                config=AwsConfig(
                    region_name=bedrock_region,
                    profile_name=bedrock_profile,
                )
            )
            bedrock_api = AwsClientFactory.build_from_boto_session(
                aws_session,
                BedrockRuntimeApi,
                client_config=Config(region_name=bedrock_region),
            )
            embeddings = LangchainEmbeddingsFactory.get_bedrock_embeddings(
                bedrock_client=bedrock_api.client,
            )
        else:
            embeddings = LangchainEmbeddingsFactory.get_huggingface_embeddings()
            bedrock_region = None
            bedrock_profile = None

        return EmbeddingConfig(
            collection_name=collection_name,
            embeddings=embeddings,
            use_bedrock=use_bedrock,
            bedrock_region=bedrock_region,
            bedrock_profile=bedrock_profile,
        )

    @staticmethod
    def get_db_config() -> DbConfig:
        db_local = os.environ["DB_LOCAL"].lower() == "true"
        if db_local:
            db_config = DbConfig(
                database=os.environ["PGVECTOR_DATABASE"],
                user=os.environ["PGVECTOR_USER"],
                password=os.environ["PGVECTOR_PASSWORD"],
                port=int(os.environ["PGVECTOR_PORT"]),
                host=os.environ["PGVECTOR_HOST"],
            )
        else:
            secretsmanager_client = AwsClientFactory.build_from_boto_session(
                AppConfigFactory.aws_session,
                SecretsManagerApi,
            )

            rds_secret_dict = secretsmanager_client.get_secret_dict(
                secret_name=os.environ["RDS_SECRET_NAME"],
            )

            if not rds_secret_dict:
                raise ValueError("RDS secret not found in Secrets Manager")

            db_config = DbConfig(
                database=rds_secret_dict["dbname"],
                user=rds_secret_dict["username"],
                password=rds_secret_dict["password"],
                port=int(rds_secret_dict["port"]),
                host=rds_secret_dict["host"],
            )

        return db_config

    @staticmethod
    def get_open_ai_config() -> Union[OpenAIConfig, None]:
        try:
            if os.environ.get("OPENAI_API_KEY"):
                api_key = api_key = os.environ["OPENAI_API_KEY"]
            else:
                openai_key_secret_name = os.environ["OPENAI_API_KEY_SECRET_NAME"]

                secretsmanager_client = AwsClientFactory.build_from_boto_session(
                    AppConfigFactory.aws_session,
                    SecretsManagerApi,
                )
                api_key = secretsmanager_client.get_secret_value(openai_key_secret_name)
                if not api_key:
                    raise ValueError("OpenAI API key not found in Secrets Manager")

            api_type = os.environ["OPENAI_API_TYPE"]
            api_version = os.environ["OPENAI_API_VERSION"]
            api_base = os.environ["OPENAI_API_BASE"]
            deployment_name = os.environ["OPENAI_DEPLOYMENT_NAME"]

            openai_config = OpenAIConfig(
                api_key=api_key,
                api_type=api_type,
                api_version=api_version,
                api_base=api_base,
                deployment_name=deployment_name,
            )
            return openai_config
        except KeyError as e:
            logger.error("Missing required OpenAI config: %s", e)
        return None

    @staticmethod
    def get_confluence_config() -> Union[ConfluenceConfig, None]:
        try:
            url = os.environ["CONFLUENCE_URL"]
            api_key = os.environ["CONFLUENCE_API_KEY"]
            username = os.environ["CONFLUENCE_USERNAME"]

            confluence_config = ConfluenceConfig(
                url=url,
                api_key=api_key,
                username=username,
            )
            return confluence_config
        except KeyError as e:
            logger.error("Missing required Confluence config: %s", e)
        return None
