from boto3.session import Session
from rag_application_framework.config.app_config import AwsConfig


class AwsSessionFactory:
    def __init__(self, config: AwsConfig):
        self._config = config

    def create_session(self) -> Session:
        return self.create_session_from_config(self._config)

    @staticmethod
    def create_session_from_config(config: AwsConfig) -> Session:
        """
        Returns a boto3 session object for the specified region
        """
        session_params = {}
        if config.region_name:
            session_params["region_name"] = config.region_name
        if config.profile_name:
            session_params["profile_name"] = config.profile_name

        return Session(**session_params)
