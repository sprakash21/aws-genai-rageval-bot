from typing import Union
from aws_cdk import Environment, Stage
from constructs import Construct
from os import name
from platform import node, python_revision
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from nc_llm_aws_infra_blocks.pre_built_stacks.app.application_stack import (
    SimpleRagAppStack,
)
from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_hugging_face.hf_sagemaker_role_stack import (
    HuggingFaceTaskType,
)


from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_aws.aws_sagemaker_endpoint_stack import (
    AwsSagemakerEndpointStack,
)
from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_hugging_face import (
    HuggingFaceSageMakerRoleStack,
    HuggingFaceSageMakerEndpointStack,
)
from nc_llm_aws_infra_blocks.pre_built_stacks.supplements.network_stack import (
    VPCNetworkStack,
)

from nc_llm_aws_infra_blocks.pre_built_stacks.app.application_stack import (
    SimpleRagAppStack,
)

from nc_llm_aws_infra_blocks.library.helpers.model_info import (
    get_sagemaker_model_info,
)


class ApplicationDeploymentBuilder:
    def __init__(
        self,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
        hugging_face_token: str,
        huggingface_model_id: str,
        huggingface_task: HuggingFaceTaskType,
        env: Environment,
        instance_type: str,
        instance_count: int,
        gpu_count: int,
        ecr_repository_name: str,
        ecr_image_tag: str,
        ecr_url: str,
        application_name: str,
        openai_api_key: str,
        app_params: dict[str, str],
        pytorch_version: Union[str, None] = None,
        repository_override: Union[str, None] = None,
        image_tag_override: Union[str, None] = None,
        app_container_vcpus: Union[int, float] = 1,
        app_container_memory: int = 2048,
    ):
        self.project_prefix = project_prefix
        self.deploy_stage = deploy_stage
        self.deploy_region = deploy_region
        self.hugging_face_token = hugging_face_token
        self.huggingface_model_id = huggingface_model_id
        self.huggingface_task = huggingface_task
        self.env = env
        self.instance_type = instance_type
        self.instance_count = instance_count
        self.gpu_count = gpu_count
        self.pytorch_version = pytorch_version
        self.repository_override = repository_override
        self.image_tag_override = image_tag_override
        self.ecr_repository_name = ecr_repository_name
        self.ecr_image_tag = ecr_image_tag
        self.ecr_url = ecr_url
        self.application_name = application_name
        self.app_params = app_params
        self.app_container_vcpus = app_container_vcpus
        self.app_container_memory = app_container_memory
        self.openai_api_key = openai_api_key

    def build(self, scope):
        llm_hf_execution_role_stack = HuggingFaceSageMakerRoleStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-hf-execution-role",
            env=self.env,
        )

        llama2_inference_stack = HuggingFaceSageMakerEndpointStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-hf-sagemaker-llama2-endpoint",
            project_prefix=self.project_prefix,
            deploy_stage=self.deploy_stage,
            deploy_region=self.deploy_region,
            huggingface_model_id=self.huggingface_model_id,
            huggingface_task=self.huggingface_task,
            huggingface_token_id=self.hugging_face_token,
            instance_type=self.instance_type,
            instance_count=self.instance_count,
            gpu_count=self.gpu_count,
            execution_role_arn=llm_hf_execution_role_stack.execution_role_arn,
            env=self.env,
            pytorch_version=self.pytorch_version,
            repository_override=self.repository_override,
            image_tag_override=self.image_tag_override,
        )

        network_stack = VPCNetworkStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-vpc",
            deploy_stage=self.deploy_stage,
            project_prefix=self.project_prefix,
            env=self.env,
        )

        swara_bot_app_stack = SimpleRagAppStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-swara-bot-app",
            env=self.env,
            vpc=network_stack.vpc,
            deploy_stage=self.deploy_stage,
            deploy_region=self.deploy_region,
            project_prefix=self.project_prefix,
            application_name=self.application_name,
            ecr_repository_name=self.ecr_repository_name,
            ecr_image_tag=self.ecr_image_tag,
            ecr_url=self.ecr_url,
            sagemaker_endpoint_name=llama2_inference_stack.hf_endpoint.ssm_parameter_endpoint_name,
            openai_api_key=self.openai_api_key,
            app_params=self.app_params,
            container_vcpus=self.app_container_vcpus,
            container_memory=self.app_container_memory,
        )


class ApplicationDeployStage(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        app_deployment_builder: ApplicationDeploymentBuilder,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        app_deployment_builder.build(self)
