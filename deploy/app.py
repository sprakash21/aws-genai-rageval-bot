#!/usr/bin/env python3

import aws_cdk as cdk

from deploy.sagemaker_studio_stack import SagemakerStudioStack
from deploy.sagemaker_llm_stack import SageMakerLLMStack
from deploy.sagemaker_huggingface_llm_stack import HuggingfaceSagemakerStack
from deploy.network_stack import VPCNetworkStack
from deploy.db_stack import DBStack

# from helpers.model_info import get_sagemaker_uris

# Environment information
aws_environment = cdk.Environment(region="eu-central-1")

# Get Model Information
# Specific to Sagemaker
# huggingface-textgeneration-falcon-7b-bf16 - textgen
# meta-textgeneration-llama-codellama-7b-python - codegen. Ireland only.
# meta-textgeneration-llama-codellama-34b-instruct - codegen instruct finetuned. Ireland only.
# TXTGEN_MODEL_ID = "meta-textgeneration-llama-codellama-7b-python"
# TXTGEN_INFERENCE_INSTANCE_TYPE = "ml.g5.2xlarge"
# textgeneration, llm, textembedding, text2text, txt2img
# Note: Some models are only available currently at some of the regions.

# TXTGEN_MODEL_TASK_TYPE = "textgeneration"
# REGION = "eu-central-1"
# model_information = get_sagemaker_uris(
#     model_id=TXTGEN_MODEL_ID,
#     model_task_type=TXTGEN_MODEL_TASK_TYPE,
#     instance_type=TXTGEN_INFERENCE_INSTANCE_TYPE,
#     region_name=REGION,
# )

app = cdk.App()
network_stack = VPCNetworkStack(app, "VPCNetworkStack", env=aws_environment)
# If sagemaker studio needs to be setup
# SagemakerStudioStack(app, "deploy", vpc=network_stack.vpc)
# If sagemaker llm app deployment and endpoint with lambda + apigw needs to be setup

# llm_stack = SageMakerLLMStack(
#     app, "llm-sm-stack", env=aws_environment, model_info=model_information
# )

#llm_stack = HuggingfaceSagemakerStack(app, "llm-hf-sm-stack", env=aws_environment)
db_stack = DBStack(app, "db-stack", vpc=network_stack.vpc, env=aws_environment)

#AppStack(
#    app,
#    "llm-app-stack",
#    env=aws_environment,
#    vpc=network_stack.vpc,
#    endpoint=llm_stack.sm_endpoint,
#)
app.synth()
