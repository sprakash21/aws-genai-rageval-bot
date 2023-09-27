import sagemaker
import boto3
from sagemaker import script_uris
from sagemaker import image_uris 
from sagemaker import model_uris
from sagemaker.jumpstart.notebook_utils import list_jumpstart_models
from sagemaker import jumpstart
boto3_session = boto3.Session(profile_name="nc-admin")
jumpstart()
session = sagemaker.Session(boto_session=boto3_session)

def get_sagemaker_uris(model_id,model_task_type,instance_type,region_name):
    FILTER = f"task == {model_task_type}"
    txt2img_models = list_jumpstart_models(region="eu-central-1")
    print(txt2img_models)
    
    MODEL_VERSION = "*"  # latest
    SCOPE = "inference"

    inference_image_uri = image_uris.retrieve(region=region_name, sagemaker_session=session, 
                                          framework=None,
                                          model_id=model_id, 
                                          model_version=MODEL_VERSION, 
                                          image_scope=SCOPE, 
                                          instance_type=instance_type)
    
    inference_model_uri = model_uris.retrieve(sagemaker_session=session, model_id=model_id, 
                                          model_version=MODEL_VERSION, 
                                          model_scope=SCOPE)
    
    inference_source_uri = script_uris.retrieve(sagemaker_session=session, model_id=model_id, 
                                            model_version=MODEL_VERSION, 
                                            script_scope=SCOPE)

    model_bucket_name = inference_model_uri.split("/")[2]
    model_bucket_key = "/".join(inference_model_uri.split("/")[3:])
    model_docker_image = inference_image_uri

    return {"model_bucket_name":model_bucket_name, "model_bucket_key": model_bucket_key, \
            "model_docker_image":model_docker_image, "instance_type":instance_type, \
                "inference_source_uri":inference_source_uri, "region_name":region_name}

TXT2IMG_MODEL_ID = "model-txt2img-stabilityai-stable-diffusion-v2-1-base"
TXT2IMG_INFERENCE_INSTANCE_TYPE = "ml.p3.2xlarge" #if your region does not support this instance type, try ml.g4dn.4xlarge 
TXT2IMG_MODEL_TASK_TYPE = "txt2img"
region_name="eu-central-1"
TXT2IMG_MODEL_INFO = get_sagemaker_uris(model_id=TXT2IMG_MODEL_ID,
                                        model_task_type=TXT2IMG_MODEL_TASK_TYPE, 
                                        instance_type=TXT2IMG_INFERENCE_INSTANCE_TYPE,
                                        region_name=region_name)
print(TXT2IMG_MODEL_INFO)
