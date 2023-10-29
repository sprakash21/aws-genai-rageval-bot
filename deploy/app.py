#!/usr/bin/env python3

from platform import node
import aws_cdk as cdk

from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.Inference.sagemaker_studio_stack import (
    SagemakerStudioStack,
)
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.Inference.sagemaker_llm_stack import (
    SageMakerLLMStack,
)
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.Inference.sagemaker_huggingface_llm_stack import (
    HuggingfaceSagemakerStack,
)
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.supplements.network_stack import (
    VPCNetworkStack,
)
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.app.db_stack import DBStack
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.app.application_stack import (
    AppStack,
)
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.supplements.developer_stack import (
    DeveloperStack,
)
from deploy.nc_llm_aws_infra_blocks.library.helpers.model_info import (
    get_sagemaker_model_info,
)

# Environment information
aws_environment = cdk.Environment(region="eu-central-1")


app = cdk.App()

chat_bot_inference_model = app.node.get_context("huggingface.llama2.13b")
hugging_face_token = app.node.get_context("huggingface.token_id")
inference_endpoint = app.node.get_context("inference_endpoint")
sagemaker_session_profile_name = app.node.get_context("sagemaker_session_profile_name")

huggingface_model_id = chat_bot_inference_model["model_id"]
huggingface_task = chat_bot_inference_model["task"]
instance_type = inference_endpoint["instance_type"]
instance_count = inference_endpoint["instance_count"]
gpu_count = inference_endpoint["gpu_count"]


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


llm_stack = HuggingfaceSagemakerStack(
    app,
    "llm-hf-sm-stack",
    env=aws_environment,
    huggingface_model_id=huggingface_model_id,
    huggingface_task=huggingface_task,
    huggingface_token_id=hugging_face_token,
    instance_type=instance_type,
    instance_count=instance_count,
    gpu_count=gpu_count,
    environment=aws_environment,
)

network_stack = VPCNetworkStack(app, "vpc-network-stack", env=aws_environment)


# ToDo: Taha: Convert to construct and put into Application Stack.
# dev_stack = DeveloperStack(
#     app, "dev-machine", vpc=network_stack.vpc, env=aws_environment
# )


db_stack = DBStack(app, "db-stack", vpc=network_stack.vpc, env=aws_environment)

app.synth()
