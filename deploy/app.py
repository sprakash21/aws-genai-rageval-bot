#!/usr/bin/env python3

import os
import aws_cdk as cdk
from build_and_deploy_pipeline import PipelineStack

from nc_llm_aws_infra_blocks.pre_built_stacks.inference.sagemaker_hugging_face.hf_sagemaker_role_stack import (
    HuggingFaceTaskType,
)

from deploy_stage import ApplicationDeploymentBuilder, InferenceType, EvaluationType

# Environment information


app = cdk.App()

chat_bot_inference_model = app.node.get_context("huggingface.llama2.13b")
hugging_face_token = app.node.get_context("huggingface.token_id")
inference_endpoint = app.node.get_context("inference_endpoint")
sagemaker_session_profile_name = app.node.get_context("sagemaker_session_profile_name")

project_prefix = app.node.get_context("project_prefix")
deploy_stage = app.node.get_context("deploy_stage")
deploy_region = app.node.get_context("deploy_region")
deploy_account = app.node.get_context("deploy_account")
app_container_vcpus = app.node.get_context("app_container_vcpus")
app_container_memory = app.node.get_context("app_container_memory")
app_params: dict[str, str] = app.node.get_context("app_params")
inference_type = app_params["INFERENCE_ENGINE"]
evaluation_type = app_params["BEDROCK_EVALUATION_ENGINE"]

if inference_type == InferenceType.BEDROCK.name.lower():
    inference_type = InferenceType.BEDROCK
elif inference_type == InferenceType.SAGEMAKER.name.lower():
    inference_type = InferenceType.SAGEMAKER
else:
    raise ValueError(f"Inference type {inference_type} is not known.")

if evaluation_type == EvaluationType.BEDROCK.name.lower():
    evaluation_type = EvaluationType.BEDROCK
elif evaluation_type == EvaluationType.SAGEMAKER.name.lower():
    evaluation_type = EvaluationType.SAGEMAKER
else:
    raise ValueError(f"EvaluationType type {evaluation_type} is not known.")


domain_name = app.node.try_get_context("domain_name")
hosted_zone_id = app.node.try_get_context("hosted_zone_id")


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

aws_environment = cdk.Environment(account=deploy_account,region=deploy_region)
app_deployment_builder = ApplicationDeploymentBuilder(
    project_prefix=project_prefix,
    deploy_stage=deploy_stage,
    deploy_account=deploy_account,
    deploy_region=deploy_region,
    hugging_face_token=hugging_face_token,
    huggingface_model_id=huggingface_model_id,
    huggingface_task=HuggingFaceTaskType.from_string(huggingface_task),
    env=aws_environment,
    inference_engine_instance_type=instance_type,
    inference_enginer_instance_count=instance_count,
    inference_enginer_gpu_count=gpu_count,
    image_tag_override=image_tag_override,
    pytorch_version=pytorch_version,
    repository_override=repository_override,
    ecr_image_tag=ecr_tag,
    ecr_repository_name=ecr_repo,
    ecr_url=ecr_url,
    application_name=project_prefix,
    app_params=app_params,
    app_container_memory=app_container_memory,
    app_container_vcpus=app_container_vcpus,
    inference_type=inference_type,
    evaluation_type=evaluation_type,
    domain_name=domain_name,
    hosted_zone_id=hosted_zone_id,
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
