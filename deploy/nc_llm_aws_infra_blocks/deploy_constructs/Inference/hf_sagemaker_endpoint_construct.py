from abc import abstractmethod
import json
from os import environ
from typing import Union
from aws_cdk import aws_sagemaker as sagemaker, CfnOutput, Environment
from constructs import Construct
from numpy import number
from base_sagemaker_endpoint_construct import BaseSageMakerEndpointConstruct

from nc_llm_aws_infra_blocks.library.config.huggingface_smconfig import (
    DEFAULT_PYTORCH_VERSION,
    region_dict,
)


# ToDo: Taha: Task is not Test Generation only, what to do here?
def get_image_uri(region, pytorch_version=DEFAULT_PYTORCH_VERSION, tgi_version="0.8.2"):
    repository = f"{region_dict[region]}.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-tgi-inference"
    tag = f"{pytorch_version}-tgi{tgi_version}-gpu-py39-cu118-ubuntu20.04"
    return f"{repository}:{tag}"


def is_gpu_instance(instance_type):
    return True if instance_type.split(".")[1][0].lower() in ["p", "g"] else False


# ToDo: Taha: Append project names
class SageMakerHFEndpointConstruct(BaseSageMakerEndpointConstruct):
    def get_container(self) -> sagemaker.CfnModel.ContainerDefinitionProperty:
        # Construct vars
        endpoint_config_name = f"config-{self.get_short_model_name()}"
        endpoint_name = f"endpoint-{self.get_short_model_name()}"

        # creates the image_uri based on the instance type and region
        image_uri = get_image_uri(region=self.huggingface_model_region)

        # defines and creates container configuration for deployment
        container_environment = {
            "HF_MODEL_ID": self.get_short_model_name(),
            "HF_TASK": self.huggingface_task,
            "HF_API_TOKEN": self.huggingface_token_id,
            "MAX_INPUT_LENGTH": json.dumps(2048),  # Max length of input text
            "MAX_TOTAL_TOKENS": json.dumps(
                4096
            ),  # Max length of the generation (including input text)
            "MAX_BATCH_TOTAL_TOKENS": json.dumps(
                8192
            ),  # Limits the number of tokens that can be processed in parallel during the generation
            "SM_NUM_GPUS": json.dumps(self.gpu_count),  # Multi GPU support
        }
        container = sagemaker.CfnModel.ContainerDefinitionProperty(
            environment=container_environment, image=image_uri
        )

        return container

    def get_short_model_name(self):
        return f'{self.model_name.replace("_","-").replace("/","--")}'

    def get_variant_name(self):
        return f"model-{self.get_short_model_name()}"

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        role_arn: str,
        instance_count: int,
        instance_type: str,
        model_name: str,
        variant_weight: float,
        huggingface_task: str,
        huggingface_token_id: str,
        gpu_count: int,
        huggingface_model_region: str,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            project_prefix,
            role_arn,
            instance_count,
            instance_type,
            model_name,
            variant_weight,
        )

        self.model_name = model_name
        self.huggingface_task = huggingface_task
        self.huggingface_token_id = huggingface_token_id
        self.huggingface_model_region = huggingface_model_region
        self.gpu_count = gpu_count

    def post_processing(self) -> None:
        # adds depends on for different resources
        self.endpoint_config.node.add_dependency(self.model)
        self.endpoint.node.add_dependency(self.endpoint_config)
