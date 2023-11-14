import json
from typing import Dict, Union

from rag_application_framework.aws.base_aws_client import BaseAwsClient
from rag_application_framework.logging.logging import Logging
from rag_application_framework.aws.base_aws_client import (
    MetaClass,
    BaseAwsClient,
    AwsServiceNameClassProperty,
)

logger = Logging.get_logger(__name__)


class SecretsManagerApi(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("secretsmanager")

    def get_secret_value(self, secret_name: str) -> Union[str, None]:
        """Retrieves the value of a secret."""
        try:
            response = self._client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except Exception as e:
            logger.error(f"Error getting secret value: {e}")
            raise

    def get_secret_dict(self, secret_name: str) -> Union[Dict, None]:
        """Retrieves the secret as a Python dictionary."""
        secret_string = self.get_secret_value(secret_name)
        if secret_string is not None:
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing secret string as JSON: {e}")
                raise
        return None
