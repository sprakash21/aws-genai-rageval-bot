import json
from abc import abstractmethod
from os import environ
from typing import Union

from aws_cdk import aws_sagemaker as sagemaker
from deploy.nc_llm_aws_infra_blocks.deploy_constructs.Inference.base_sagemaker_endpoint_construct import (
    BaseSageMakerEndpointConstruct,
)
from constructs import Construct
from nc_llm_aws_infra_blocks.library.config.huggingface_smconfig import (
    DEFAULT_PYTORCH_VERSION,
    region_dict,
)

# ToDo: Taha: Append project names


class AwsSagemakerEndpointConstruct(BaseSageMakerEndpointConstruct):
    """SageMaker Endpoint Construction with custom configurations"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
        role_arn: str,
        instance_count: int,
        instance_type: str,
        model_name: str,
        variant_weight: float,
        model_bucket_name: str,
        model_bucket_key: str,
        model_docker_image: str,
        sagemaker_region: str,
    ) -> None:
        """Initialize the SageMakerEndpointConstruct class."""
        super().__init__(
            scope,
            construct_id,
            project_prefix,
            deploy_stage,
            deploy_region,
            role_arn,
            instance_count,
            instance_type,
            model_name,
            variant_weight,
        )

        self._set_custom_parameters(
            model_bucket_name, model_bucket_key, model_docker_image, sagemaker_region
        )

    def _set_custom_parameters(
        self,
        model_bucket_name: str,
        model_bucket_key: str,
        model_docker_image: str,
        sagemaker_region: str,
    ) -> None:
        """Private helper method to set custom parameters."""
        self.model_bucket_name = model_bucket_name
        self.model_bucket_key = model_bucket_key
        self.model_docker_image = model_docker_image
        self.sagemaker_region = sagemaker_region

    def get_container(self) -> sagemaker.CfnModel.ContainerDefinitionProperty:
        """Get container definition for the SageMaker endpoint."""
        environment = self._get_container_environment()
        return sagemaker.CfnModel.ContainerDefinitionProperty(
            image=self.model_docker_image,
            model_data_url=f"s3://{self.model_bucket_name}/{self.model_bucket_key}",
            environment=environment,
        )

    def _get_container_environment(self) -> dict:
        """Private helper method to get container environment variables."""
        return {
            "SAGEMAKER_ENV": "1",
            "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
            "SAGEMAKER_MODEL_SERVER_WORKERS": "1",
            "SAGEMAKER_REGION": self.sagemaker_region,
        }
