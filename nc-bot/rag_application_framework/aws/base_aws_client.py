from abc import abstractclassmethod
from botocore.client import BaseClient
from botocore.config import Config


class AwsServiceNameClassProperty:
    def __init__(self, value=None):
        self._service_name = value

    def __get__(self, instance, owner):
        return self._service_name


class MetaClass(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        for key, value in dct.items():
            if isinstance(value, AwsServiceNameClassProperty):
                setattr(new_class, key, value)
        return new_class


class BaseAwsClient(metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty()

    def __init__(
        self,
        client: BaseClient,
    ):
        self._client = client

    @property
    def client(self) -> BaseClient:
        return self._client

    @classmethod
    def get_client_config(cls) -> Config:
        return Config()
