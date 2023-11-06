# Adapted from Huggingface documentation.
# WIP..
from enum import Enum
from typing import Text, Union
from aws_cdk import Environment, aws_iam as iam, aws_sagemaker as sagemaker, Stack
from nc_llm_aws_infra_blocks.deploy_constructs.inference.hf_sagemaker_endpoint_construct import (
    HuggingFaceTaskType,
)
from nc_llm_aws_infra_blocks.deploy_constructs.inference.hf_sagemaker_endpoint_construct import (
    HuggingFaceSagemakerEndpointConstruct,
)
from constructs import Construct


# ToDo: Taha: Append project names
class HuggingFaceSageMakerEndpointStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
        execution_role_arn: str,
        gpu_count: int,
        huggingface_token_id: str,
        huggingface_model_id: str = "meta-llama/Llama-2-13b-chat-hf",
        huggingface_task: HuggingFaceTaskType = HuggingFaceTaskType.TextGeneration,
        instance_type: str = "ml.g5.12xlarge",
        instance_count: int = 1,
        initial_variant_weight: float = 1,
        pytorch_version: Union[str, None] = None,
        repository_override: Union[str, None] = None,
        image_tag_override: Union[str, None] = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ToDo: Taha: Parameterize properly like e.g. variant_weight
        self.endpoint = HuggingFaceSagemakerEndpointConstruct(
            self,
            "sm-hf-ep",
            model_name=huggingface_model_id,
            project_prefix=project_prefix,
            deploy_stage=deploy_stage,
            deploy_region=deploy_region,
            huggingface_task=huggingface_task,
            huggingface_token_id=huggingface_token_id,
            role_arn=execution_role_arn,
            instance_type=instance_type,
            gpu_count=gpu_count,
            instance_count=instance_count,
            variant_weight=initial_variant_weight,
            pytorch_version=pytorch_version,
            repository_override=repository_override,
            image_tag_override=image_tag_override,
        )

    @property
    def sm_endpoint(self) -> HuggingFaceSagemakerEndpointConstruct:
        return self.endpoint
