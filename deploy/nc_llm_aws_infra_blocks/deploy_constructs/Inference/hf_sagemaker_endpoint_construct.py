from aws_cdk import aws_sagemaker as sagemaker
from deploy.nc_llm_aws_infra_blocks.deploy_constructs.Inference.base_sagemaker_endpoint_construct import (
    BaseSageMakerEndpointConstruct,
)
from constructs import Construct
from deploy.nc_llm_aws_infra_blocks.pre_built_stacks.Inference.sagemaker_hugging_face.hf_sagemaker_endpoint_stack import (
    HuggingFaceTaskType,
)
from nc_llm_aws_infra_blocks.library.config.huggingface_smconfig import (
    DEFAULT_PYTORCH_VERSION,
    region_dict,
)


# ToDo: Taha: Task is not Text Generation only, what to do here?
def get_image_uri(region, pytorch_version=DEFAULT_PYTORCH_VERSION, tgi_version="0.8.2"):
    repository = f"{region_dict[region]}.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-tgi-inference"
    tag = f"{pytorch_version}-tgi{tgi_version}-gpu-py39-cu118-ubuntu20.04"
    return f"{repository}:{tag}"


# ToDo: Taha: Append project names
class HuggingFaceSagemakerEndpointConstruct(BaseSageMakerEndpointConstruct):
    """SageMaker Endpoint Construction for Hugging Face models"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
        role_arn: str,
        instance_count: int,
        instance_type: str,
        model_name: str,
        variant_weight: float,
        huggingface_task: HuggingFaceTaskType,
        huggingface_token_id: str,
        gpu_count: int,
    ) -> None:
        """Initialize the SageMakerHFEndpointConstruct class."""
        super().__init__(
            scope,
            construct_id,
            project_prefix,
            deploy_stage,
            deploy_region,
            role_arn,
            instance_count,
            instance_type,
            model_name,
            variant_weight,
        )

        self.huggingface_task = huggingface_task
        self.huggingface_token_id = huggingface_token_id
        self.gpu_count = gpu_count

    def get_container(self) -> sagemaker.CfnModel.ContainerDefinitionProperty:
        """Get container definition for the SageMaker Hugging Face endpoint."""
        container_environment = self._get_container_environment()
        image_uri = self._get_image_uri()
        return sagemaker.CfnModel.ContainerDefinitionProperty(
            environment=container_environment, image=image_uri
        )

    def _get_container_environment(self) -> dict:
        """Private helper method to get container environment variables."""
        return {
            "HF_MODEL_ID": self.model_name,
            "HF_TASK": self.huggingface_task.value,
            "HF_API_TOKEN": self.huggingface_token_id,
            "MAX_INPUT_LENGTH": str(2048),
            "MAX_TOTAL_TOKENS": str(4096),
            "MAX_BATCH_TOTAL_TOKENS": str(8192),
            "SM_NUM_GPUS": str(self.gpu_count),
        }

    def _get_image_uri(self) -> str:
        """Private helper method to get image URI for container."""
        return get_image_uri(region=self.deploy_region)

    def post_processing(self) -> None:
        super().post_processing()
        self.endpoint_config.node.add_dependency(self.model)
        self.endpoint.node.add_dependency(self.endpoint_config)
