import sagemaker
import boto3
from sagemaker import script_uris
from sagemaker import image_uris
from sagemaker import model_uris
from dataclasses import dataclass


@dataclass
class SageMakerModelInfo:
    model_bucket_name: str
    model_bucket_key: str
    model_docker_image: str
    instance_type: str
    inference_source_uri: str
    region_name: str


def get_sagemaker_model_info(
    model_id,
    model_task_type,
    instance_type,
    region_name,
    profile_name,
    model_version="*",
    scope="inference",
) -> SageMakerModelInfo:
    FILTER = f"task == {model_task_type}"
    boto3_session = boto3.Session(profile_name=profile_name, region_name=region_name)
    session = sagemaker.Session(boto_session=boto3_session)

    inference_image_uri = image_uris.retrieve(
        region=region_name,
        framework=None,
        model_id=model_id,
        model_version=model_version,
        image_scope=scope,
        instance_type=instance_type,
    )

    inference_model_uri = model_uris.retrieve(
        sagemaker_session=session,
        model_id=model_id,
        model_version=model_version,
        model_scope=scope,
    )

    inference_source_uri = script_uris.retrieve(
        sagemaker_session=session,
        model_id=model_id,
        model_version=model_version,
        script_scope=scope,
    )

    model_bucket_name = inference_model_uri.split("/")[2]
    model_bucket_key = "/".join(inference_model_uri.split("/")[3:])
    model_docker_image = inference_image_uri

    return SageMakerModelInfo(
        model_bucket_name,
        model_bucket_key,
        model_docker_image,
        instance_type,
        inference_source_uri,
        region_name,
    )
