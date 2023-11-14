from curses import meta
from botocore.config import Config
from rag_application_framework.aws.base_aws_client import (
    MetaClass,
    BaseAwsClient,
    AwsServiceNameClassProperty,
)


class BedrockApi(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("bedrock")

    _service_name = "bedrock"

    @classmethod
    def get_client_config(
        cls,
    ) -> Config:
        boto3_client_config = Config(
            retries={
                "max_attempts": 10,
                "mode": "standard",
            },
        )
        return boto3_client_config
