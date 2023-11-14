from typing import Union

from rag_application_framework.aws.base_aws_client import BaseAwsClient
from rag_application_framework.logging.logging import Logging
from rag_application_framework.aws.base_aws_client import (
    MetaClass,
    BaseAwsClient,
    AwsServiceNameClassProperty,
)

logger = Logging.get_logger(__name__)


class SsmApi(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("ssm")

    def get_parameter(
        self, name: str, with_decryption: bool = True
    ) -> Union[str, None]:
        """Retrieves the value of a parameter."""
        try:
            response = self._client.get_parameter(
                Name=name, WithDecryption=with_decryption
            )
            return response["Parameter"]["Value"]
        except Exception as e:
            logger.error(f"Error getting parameter: {e}")
            raise
