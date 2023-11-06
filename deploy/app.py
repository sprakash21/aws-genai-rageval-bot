#!/usr/bin/env python3

from os import name
from platform import node
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from nc_llm_aws_infra_blocks.pre_built_stacks.app.application_stack import (
    SimpleRagAppStack,
)
from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_hugging_face.hf_sagemaker_role_stack import (
    HuggingFaceTaskType,
)

from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_studio_stack import (
    SagemakerStudioStack,
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
from nc_llm_aws_infra_blocks.pre_built_stacks.supplements.developer_stack import (
    DeveloperStack,
)
from nc_llm_aws_infra_blocks.library.helpers.model_info import (
    get_sagemaker_model_info,
)

# Environment information


app = cdk.App()

chat_bot_inference_model = app.node.get_context("huggingface.llama2.13b")
hugging_face_token = app.node.get_context("huggingface.token_id")
inference_endpoint = app.node.get_context("inference_endpoint")
sagemaker_session_profile_name = app.node.get_context("sagemaker_session_profile_name")

project_prefix = app.node.get_context("project_prefix")
deploy_stage = app.node.get_context("deploy_stage")
deploy_region = app.node.get_context("deploy_region")


huggingface_model_id = chat_bot_inference_model["model_id"]
huggingface_task = chat_bot_inference_model["task"]
instance_type = inference_endpoint["instance_type"]
instance_count = inference_endpoint["instance_count"]
gpu_count = inference_endpoint["gpu_count"]

aws_environment = cdk.Environment(region=deploy_region)


# TXTGEN_MODEL_ID = "meta-textgeneration-llama-2-7b-f"
# TXTGEN_INFERENCE_INSTANCE_TYPE = "ml.g5.2xlarge"
# TXTGEN_MODEL_TASK_TYPE = "textgeneration"
# REGION = "eu-central-1"
# model_information = get_sagemaker_model_info(
#     model_id=TXTGEN_MODEL_ID,
#     model_task_type=TXTGEN_MODEL_TASK_TYPE,
#     instance_type=TXTGEN_INFERENCE_INSTANCE_TYPE,
#     region_name=aws_environment.region,
#     profile_name=sagemaker_session_profile_name,
# )
# llm_stack = SageMakerLLMStack(
#     app, "llm-sm-stack", env=aws_environment, model_info=model_information
# )

# If sagemaker studio needs to be setup
# SagemakerStudioStack(app, "deploy", vpc=network_stack.vpc)
# If sagemaker llm app deployment and endpoint with lambda + apigw needs to be setup

llm_hf_execution_role_stack = HuggingFaceSageMakerRoleStack(
    app,
    f"{project_prefix}-{deploy_stage}-hf-execution-role",
    env=aws_environment,
)

llama2_inference_stack = HuggingFaceSageMakerEndpointStack(
    app,
    f"{project_prefix}-{deploy_stage}-hf-sagemaker-llama2-endpoint",
    project_prefix=project_prefix,
    deploy_stage=deploy_stage,
    deploy_region=deploy_region,
    huggingface_model_id=huggingface_model_id,
    huggingface_task=HuggingFaceTaskType.from_string("text-generation"),
    huggingface_token_id=hugging_face_token,
    instance_type=instance_type,
    instance_count=instance_count,
    gpu_count=gpu_count,
    environment=aws_environment,
    execution_role_arn=llm_hf_execution_role_stack.execution_role_arn,
    env=aws_environment,
)


llama2_inference_stack.node.add_dependency(llm_hf_execution_role_stack)

network_stack = VPCNetworkStack(
    app,
    f"{project_prefix}-{deploy_stage}-vpc",
    deploy_stage=deploy_stage,
    project_prefix=project_prefix,
    env=aws_environment,
)


swara_bot_app_stack = SimpleRagAppStack(
    app,
    f"{project_prefix}-{deploy_stage}-swara-bot-app",
    env=aws_environment,
    vpc=network_stack.vpc,
)

app.synth()
