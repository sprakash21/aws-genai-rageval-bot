import hmac, hashlib, base64
from enum import Enum

from rag_application_framework.aws.base_aws_client import MetaClass, BaseAwsClient, AwsServiceNameClassProperty
from rag_application_framework.logging.logging import Logging

logger = Logging.get_logger(__name__)


def _generate_secret_hash(username: str, client_id: str, app_secret: str) -> str:
    message = bytes(username + client_id, 'utf-8')
    key = bytes(app_secret, 'utf-8')
    secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()
    return secret_hash


class AuthType(Enum):
    USER_PASSWORD_AUTH = "USER_PASSWORD_AUTH"
    REFRESH_TOKEN_AUTH = "REFRESH_TOKEN_AUTH"


class CognitoIdpApi(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("cognito-idp")

    def initiate_authentication(self,
                                username: str,
                                password: str,
                                client_id: str,
                                client_secret: str) -> dict | None:
        """Initiate Authentication to Cognito Service."""
        try:
            response = self._client.initiate_auth(AuthFlow="USER_PASSWORD_AUTH",
                                                  AuthParameters={"USERNAME": username,
                                                                  "PASSWORD": password,
                                                                  "SECRET_HASH": _generate_secret_hash(
                                                                      username,
                                                                      client_id,
                                                                      client_secret
                                                                  )},
                                                  ClientId=client_id)
            return response
        except Exception as e:
            logger.error(f"Error initiating authentication for the user {username}")
            logger.error(f"Error stack is {e}")
            raise
