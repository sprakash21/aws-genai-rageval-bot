#!/usr/bin/env python3

import aws_cdk as cdk

from deploy.sagemaker_studio_stack import SagemakerStudioStack
from deploy.sagemaker_llm_stack import SageMakerLLMStack
from deploy.application_stack import AppStack
from deploy.network_stack import VPCNetworkStack
from helpers.model_info import get_sagemaker_uris

# Environment information
aws_environment = {"region": "eu-central-1"}

# Get Model Information
TXT2IMG_MODEL_ID = "meta-textgeneration-llama-codellama-34b-instruct"
TXT2IMG_INFERENCE_INSTANCE_TYPE = "ml.g5.24xlarge"
# textgeneration, llm, textembedding, text2text, txt2img
# meta-textgeneration-llama-codellama-7b-python
TXT2IMG_MODEL_TASK_TYPE = "textgeneration"
region_name="eu-central-1"
model_information = get_sagemaker_uris(model_id=TXT2IMG_MODEL_ID,
                                        model_task_type=TXT2IMG_MODEL_TASK_TYPE, 
                                        instance_type=TXT2IMG_INFERENCE_INSTANCE_TYPE,
                                        region_name=region_name)

app = cdk.App()
network_stack = VPCNetworkStack(app, "VPCNetworkStack", env=aws_environment)
# If sagemaker studio needs to be setup
#SagemakerStudioStack(app, "deploy", vpc=network_stack.vpc)
# If sagemaker llm app deployment and endpoint with lambda + apigw needs to be setup
AppStack(app, "llm-app-stack", env=aws_environment, vpc=network_stack.vpc)
SageMakerLLMStack(app, "llm-sm-stack", env=aws_environment, model_info=model_information)

app.synth()
