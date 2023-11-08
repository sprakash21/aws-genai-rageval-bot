#!/usr/bin/env python3

from os import name
from platform import node, python_revision
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from build_and_deploy_pipeline import PipelineStack

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

from deploy_stage import ApplicationDeploymentBuilder

# Environment information


app = cdk.App()

chat_bot_inference_model = app.node.get_context("huggingface.llama2.13b")
hugging_face_token = app.node.get_context("huggingface.token_id")
inference_endpoint = app.node.get_context("inference_endpoint")
sagemaker_session_profile_name = app.node.get_context("sagemaker_session_profile_name")

project_prefix = app.node.get_context("project_prefix")
deploy_stage = app.node.get_context("deploy_stage")
deploy_region = app.node.get_context("deploy_region")
openai_api_key = app.node.get_context("openai_api_key")
use_bedrock = app.node.get_context("use_bedrock")
bedrock_region = app.node.get_context("bedrock_region")
app_container_vcpus = app.node.get_context("app_container_vcpus")
app_container_memory = app.node.get_context("app_container_memory")


ecr_repo = app.node.try_get_context("ecr_repo")
ecr_tag = app.node.try_get_context("ecr_image_tag")
ecr_url = app.node.try_get_context("ecr_url")

deploy_pipeline = app.node.try_get_context("deploy_pipeline")


huggingface_model_id = chat_bot_inference_model["model_id"]
huggingface_task = chat_bot_inference_model["task"]
pytorch_version = chat_bot_inference_model.get("pytorch_version")
repository_override = chat_bot_inference_model.get("repository_override")
image_tag_override = chat_bot_inference_model.get("image_tag_override")

instance_type = inference_endpoint["instance_type"]
instance_count = inference_endpoint["instance_count"]
gpu_count = inference_endpoint["gpu_count"]


aws_environment = cdk.Environment(region=deploy_region)

app_deployment_builder = ApplicationDeploymentBuilder(
    project_prefix=project_prefix,
    deploy_stage=deploy_stage,
    deploy_region=deploy_region,
    hugging_face_token=hugging_face_token,
    huggingface_model_id=huggingface_model_id,
    huggingface_task=HuggingFaceTaskType.from_string(huggingface_task),
    env=aws_environment,
    instance_type=instance_type,
    instance_count=instance_count,
    gpu_count=gpu_count,
    image_tag_override=image_tag_override,
    pytorch_version=pytorch_version,
    repository_override=repository_override,
    ecr_image_tag=ecr_tag,
    ecr_repository_name=ecr_repo,
    ecr_url=ecr_url,
    application_name=project_prefix,
    openai_api_key=openai_api_key,
    use_bedrock=use_bedrock,
    bedrock_region=bedrock_region,
    app_container_memory=app_container_memory,
    app_container_vcpus=app_container_vcpus,
)

if not deploy_pipeline:
    app_deployment_builder.build(app)
else:
    PipelineStack(
        app,
        f"{project_prefix}-{deploy_stage}-pipeline",
        project_prefix=project_prefix,
        deploy_stage=deploy_stage,
        docker_image_name="llama2-13b-chatbot",
        code_commit_repo_name="llama2-13b-chatbot",
        app_deployment_builder=app_deployment_builder,
        env=aws_environment,
    )


app.synth()
