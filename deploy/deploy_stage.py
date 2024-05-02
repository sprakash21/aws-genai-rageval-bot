from math import inf
from typing import Union
import cdk_nag
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

from enum import Enum


class InferenceType(Enum):
    SAGEMAKER = "sagemaker"
    BEDROCK = "bedrock"


class EvaluationType(Enum):
    SAGEMAKER = "sagemaker"
    BEDROCK = "bedrock"


class ApplicationDeploymentBuilder:
    def __init__(
        self,
        project_prefix: str,
        deploy_stage: str,
        deploy_account:str,
        deploy_region: str,
        env: Environment,
        ecr_repository_name: str,
        ecr_image_tag: str,
        ecr_url: str,
        application_name: str,
        app_params: dict[str, str],
        inference_type: InferenceType,
        evaluation_type: EvaluationType,
        app_container_vcpus: Union[int, float] = 1,
        app_container_memory: int = 2048,
        domain_name: Union[str, None] = None,
        hosted_zone_id: Union[str, None] = None,
        inference_engine_instance_type: Union[str, None] = None,
        inference_enginer_instance_count: Union[int, None] = None,
        inference_enginer_gpu_count: Union[int, None] = None,
        hugging_face_token: Union[str, None] = None,
        huggingface_model_id: Union[str, None] = None,
        huggingface_task: Union[HuggingFaceTaskType, None] = None,
        pytorch_version: Union[str, None] = None,
        repository_override: Union[str, None] = None,
        image_tag_override: Union[str, None] = None,
    ):
        self.project_prefix = project_prefix
        self.deploy_stage = deploy_stage
        self.deploy_account = deploy_account
        self.deploy_region = deploy_region
        self.hugging_face_token = hugging_face_token
        self.huggingface_model_id = huggingface_model_id
        self.huggingface_task = huggingface_task
        self.env = env
        self.instance_type = inference_engine_instance_type
        self.instance_count = inference_enginer_instance_count
        self.gpu_count = inference_enginer_gpu_count
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
        self.inference_type = inference_type
        self.evaluation_type = evaluation_type
        self.domain_name = domain_name
        self.hosted_zone_id = hosted_zone_id

    def build(self, scope):
        if self.inference_type == InferenceType.SAGEMAKER:
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

            sagemaker_endpoint_name = (
                llama2_inference_stack.hf_endpoint.ssm_parameter_endpoint_name
            )
        else:
            sagemaker_endpoint_name = None

        network_stack = VPCNetworkStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-vpc",
            deploy_stage=self.deploy_stage,
            project_prefix=self.project_prefix,
            env=self.env,
        )

        qa_bot_app_stack = SimpleRagAppStack(
            scope,
            f"{self.project_prefix}-{self.deploy_stage}-bot-app",
            vpc=network_stack.vpc,
            deploy_stage=self.deploy_stage,
            env=self.env,
            account=self.deploy_account,
            deploy_region=self.deploy_region,
            project_prefix=self.project_prefix,
            application_name=self.application_name,
            ecr_repository_name=self.ecr_repository_name,
            ecr_image_tag=self.ecr_image_tag,
            ecr_url=self.ecr_url,
            sagemaker_endpoint_name=sagemaker_endpoint_name,
            app_params=self.app_params,
            container_vcpus=self.app_container_vcpus,
            container_memory=self.app_container_memory,
            domain_name=self.domain_name,
            hosted_zone_id=self.hosted_zone_id,
        )
        # Supressions for cdk_nag at stack level
        cdk_nag.NagSuppressions.add_stack_suppressions(
            qa_bot_app_stack,
            [
                # Fixed
                # cdk_nag.NagPackSuppression(
                #    id="AwsSolutions-SMG4", reason="Not required"
                # ),
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-RDS6", reason="No need for IAM Auth"
                ),
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-ECS2",
                    reason="The environment variables are configurations used",
                ),
                # ECR AuthorizationToken needs to be on all resources with *
                # Reference: 
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-IAM5",
                    applies_to=["Resource::*",{"regex":"/^Resource::.*/g"}],
                    reason="ECR AuthorizationToken needs to be on all resources with * and S3 bucket needs wildcard also on resource",
                ),
                # The main stack has no direct relation with the wildcards on granular resources.
                # This is internally required for the elbv2 setup for creation the access logs and hence supressed.
                #cdk_nag.NagPackSuppression(
                #    id="AwsSolutions-IAM5",
                #    reason="Resource supression is added to supress on granular * resources",
                #),
                #cdk_nag.NagPackSuppression(
                #    id="AwsSolutions-IAM5",
                #    reason="""
                #    The main stack has no direct relation with the wildcards on granular resources.
                #    This is internally required for the elbv2 setup for creation the access logs and hence supressed.
                #    """,
                #    applies_to=["Action::s3:Abort*",
                #    "Action::s3:DeleteObject*",
                #    "Action::s3:GetBucket*",
                #    "Action::s3:GetObject*",
                #    "Action::s3:List*",
                #    "Resource::*"]
                #),
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-EC23",
                    reason="""This is a false alarm raised from the cdk-nag for load_balancer. Load_balancer is designed in a way that all traffic is coming into it on the designated port\n
                           Check the recommended rules: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-update-security-groups.html#security-group-recommended-rules""",
                ),
                cdk_nag.NagPackSuppression(
                    id="AwsSolutions-S1",
                    reason="""We are only using S3 bucket to upload and use the pdf-file from the UI
                           for the demo application and there is no need for server access logs to be enabled""",
                ),
                #Fixed by adding access_logs support
                #cdk_nag.NagPackSuppression(
                #    id="AwsSolutions-ELB2",
                #    reason="Supressing the rule as it is not required for the demo purposes",
                #),
            ],
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
