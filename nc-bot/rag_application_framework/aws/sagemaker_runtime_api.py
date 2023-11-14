from rag_application_framework.aws.base_aws_client import BaseAwsClient
from rag_application_framework.logging.logging import Logging
from rag_application_framework.aws.base_aws_client import (
    MetaClass,
    BaseAwsClient,
    AwsServiceNameClassProperty,
)

logger = Logging.get_logger(__name__)


class SagemakerRuntimeApi(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("sagemaker-runtime")
