from abc import abstractmethod
from typing import Union
from aws_cdk import aws_sagemaker as sagemaker, CfnOutput
from constructs import Construct
from deploy.nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct


class BaseSageMakerEndpointConstruct(BaseConstruct):
    """Base class for SageMaker Endpoint Construction"""

    @abstractmethod
    def get_container(self) -> sagemaker.CfnModel.ContainerDefinitionProperty:
        """Abstract method to get container definition."""
        raise NotImplementedError()

    @abstractmethod
    def get_variant_name(self) -> str:
        """Abstract method to get variant name."""
        return self.model_name

    def post_processing(self) -> None:
        """Placeholder for post processing tasks."""
        pass

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
        initial_variant_weight: float,
    ):
        super().__init__(
            scope=scope,
            id=construct_id,
            project_prefix=project_prefix,
            deploy_stage=deploy_stage,
            deploy_region=deploy_region,
        )

        self.model_name = model_name

        self.model = sagemaker.CfnModel(
            self,
            f"hf-model",
            execution_role_arn=role_arn,
            primary_container=self.get_container(),
            model_name=f"{self.resource_prefix}-model",
        )

        self.endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            f"hf-sagemaker-endpoint-config",
            endpoint_config_name=f"{self.resource_prefix}-endpointpconfig",
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
            f"hf-sagemaker-endpoint",
            endpoint_name=f"{self.resource_prefix}-endpoint",
            endpoint_config_name=self.endpoint_config.attr_endpoint_config_name,
        )

        CfnOutput(
            scope=self,
            id=f"{self.resource_prefix}-EndpointOutput",
            value=str(self.endpoint.endpoint_name),
        )

        self.post_processing()

    @property
    def attr_endpoint_name(self) -> str:
        return self.endpoint.attr_endpoint_name

    @property
    def endpoint_name(self) -> Union[str, None]:
        return self.endpoint.endpoint_name
