from typing import Type, TypeVar, Union

import boto3
from botocore.config import Config
from rag_application_framework.aws.base_aws_client import BaseAwsClient

_TAwsClient = TypeVar("_TAwsClient", bound=BaseAwsClient)


class AwsClientFactory:
    @staticmethod
    def build_from_boto_session(
        session: boto3.Session,
        service_api_type: Type[_TAwsClient],
        client_config: Union[Config, None] = None,
    ) -> _TAwsClient:
        if not client_config:
            client_config = Config()

        client_config = service_api_type.get_client_config().merge(client_config)

        client = session.client(
            service_name=service_api_type.service_name, config=client_config
        )
        return service_api_type(client=client)
