import json
from aws_cdk import aws_sagemaker as sagemaker, CfnOutput, Environment
from constructs import Construct

from nc_llm_aws_infra_blocks.library.config.huggingface_smconfig import LATEST_PYTORCH_VERSION, region_dict


class SageMakerEndpointConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        role_arn: str,
        model_name: str,
        model_bucket_name: str,
        model_bucket_key: str,
        model_docker_image: str,
        variant_name: str,
        variant_weight: int,
        instance_count: int,
        instance_type: str,
        environment: dict,
        deploy_enable: bool,
    ) -> None:
        super().__init__(scope, construct_id)

        model = sagemaker.CfnModel(
            self,
            f"{model_name}-Model",
            execution_role_arn=role_arn,
            containers=[
                sagemaker.CfnModel.ContainerDefinitionProperty(
                    image=model_docker_image,
                    model_data_url=f"s3://{model_bucket_name}/{model_bucket_key}",
                    environment=environment,
                )
            ],
            model_name=f"{project_prefix}-{model_name}-Model",
        )

        config = sagemaker.CfnEndpointConfig(
            self,
            f"{model_name}-Config",
            endpoint_config_name=f"{project_prefix}-{model_name}-Config",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=model.attr_model_name,
                    variant_name=variant_name,
                    initial_variant_weight=variant_weight,
                    initial_instance_count=instance_count,
                    instance_type=instance_type,
                )
            ],
        )

        self.deploy_enable = deploy_enable
        if deploy_enable:
            self.endpoint = sagemaker.CfnEndpoint(
                self,
                f"{model_name}-Endpoint",
                endpoint_name=f"{project_prefix}-{model_name}-Endpoint",
                endpoint_config_name=config.attr_endpoint_config_name,
            )

            CfnOutput(
                scope=self,
                id=f"{model_name}EndpointName",
                value=self.endpoint.endpoint_name,
            )

    @property
    def endpoint_name(self) -> str:
        return (
            self.endpoint.attr_endpoint_name
            if self.deploy_enable
            else "not_yet_deployed"
        )


# Task is now default to text-generation.
def get_image_uri(
    region=None, pytorch_version=LATEST_PYTORCH_VERSION, tgi_version="1.1.0"
):
    repository = f"{region_dict[region]}.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-tgi-inference"
    tag = f"{pytorch_version}-tgi{tgi_version}-gpu-py39-cu118-ubuntu20.04"
    return f"{repository}:{tag}"


def is_gpu_instance(instance_type):
    return True if instance_type.split(".")[1][0].lower() in ["p", "g"] else False


class SageMakerHFEndpointConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        env: Environment,
        huggingface_model: str,
        huggingface_task: str,
        huggingface_token_id: str,
        execution_role_arn: str,
        instance_type: str,
    ) -> None:
        super().__init__(scope, construct_id)

        # Construct vars
        model_name = f'model-{huggingface_model.replace("_","-").replace("/","--")}'
        endpoint_config_name = (
            f'config-{huggingface_model.replace("_","-").replace("/","--")}'
        )
        endpoint_name = (
            f'endpoint-{huggingface_model.replace("_","-").replace("/","--")}'
        )

        # creates the image_uri based on the instance type and region
        image_uri = get_image_uri(region=env.region)

        # defines and creates container configuration for deployment
        container_environment = {
            "HF_MODEL_ID": huggingface_model,
            "HF_TASK": huggingface_task,
            "HF_API_TOKEN": huggingface_token_id,
            "MAX_INPUT_LENGTH": json.dumps(2048),  # Max length of input text
            "MAX_TOTAL_TOKENS": json.dumps(
                4096
            ),  # Max length of the generation (including input text)
            "MAX_BATCH_TOTAL_TOKENS": json.dumps(
                8192
            ),  # Limits the number of tokens that can be processed in parallel during the generation
            "SM_NUM_GPUS": json.dumps(1),  # Single GPU support
            # Quantization
            #'HF_MODEL_QUANTIZE' : 'gptq',
        }
        container = sagemaker.CfnModel.ContainerDefinitionProperty(
            environment=container_environment, image=image_uri
        )

        # creates SageMaker Model Instance
        model = sagemaker.CfnModel(
            self,
            "hf_model",
            execution_role_arn=execution_role_arn,
            primary_container=container,
            model_name=model_name,
        )

        # Creates SageMaker Endpoint configurations
        endpoint_configuration = sagemaker.CfnEndpointConfig(
            self,
            "hf_endpoint_config",
            endpoint_config_name=endpoint_config_name,
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_instance_count=1,
                    instance_type=instance_type,
                    model_name=model.model_name,
                    initial_variant_weight=1.0,
                    variant_name=model.model_name,
                )
            ],
        )
        # Creates Real-Time Endpoint
        endpoint = sagemaker.CfnEndpoint(
            self,
            "hf_endpoint",
            endpoint_name=endpoint_name,
            endpoint_config_name=endpoint_configuration.endpoint_config_name,
        )

        # adds depends on for different resources
        endpoint_configuration.node.add_dependency(model)
        endpoint.node.add_dependency(endpoint_configuration)

        # construct export values
        self.endpoint_name = endpoint.endpoint_name
