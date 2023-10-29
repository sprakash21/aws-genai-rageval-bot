from abc import abstractmethod
import json
from os import environ
from typing import Union
from aws_cdk import aws_sagemaker as sagemaker, CfnOutput, Environment
from constructs import Construct
from numpy import number

from nc_llm_aws_infra_blocks.library.config.huggingface_smconfig import (
    DEFAULT_PYTORCH_VERSION,
    region_dict,
)


class BaseSageMakerEndpointConstruct(Construct):
    @abstractmethod
    def get_container(self) -> sagemaker.CfnModel.ContainerDefinitionProperty:
        raise NotImplementedError()

    def get_variant_name(self) -> str:
        return self.model_name

    @staticmethod
    def make_model_friendly_name(model_name) -> str:
        return model_name

    def post_processing(self) -> None:
        pass

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        role_arn: str,
        instance_count: int,
        instance_type: str,
        model_name: str,
        initial_variant_weight: float,
    ):
        self.model_name = model_name

        self.model = sagemaker.CfnModel(
            self,
            f"{model_name}-Model",
            execution_role_arn=role_arn,
            primary_container=self.get_container(),
            model_name=f"{project_prefix}-{model_name}-Model",
        )

        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            f"{model_name}-Config",
            endpoint_config_name=f"{project_prefix}-{model_name}-Config",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=self.model.attr_model_name,
                    variant_name=self.get_variant_name(),
                    initial_variant_weight=initial_variant_weight,
                    initial_instance_count=instance_count,
                    instance_type=instance_type,
                )
            ],
        )

        self.endpoint = sagemaker.CfnEndpoint(
            self,
            f"{model_name}-Endpoint",
            endpoint_name=f"{project_prefix}-{model_name}-Endpoint",
            endpoint_config_name=self.endpoint_config.attr_endpoint_config_name,
        )

        CfnOutput(
            scope=self,
            id=f"{model_name}EndpointName",
            value=str(self.endpoint.endpoint_name),
        )

    @property
    def attr_endpoint_name(self) -> str:
        return self.endpoint.attr_endpoint_name

    @property
    def endpoint_name(self) -> Union[str, None]:
        return self.endpoint.endpoint_name
