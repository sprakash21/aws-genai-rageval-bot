# Adapted from Huggingface documentation.
# WIP..
from aws_cdk import Environment, aws_iam as iam, aws_sagemaker as sagemaker, Stack
from deploy.nc_llm_aws_infra_blocks.deploy_constructs.Inference.hf_sagemaker_endpoint_construct import (
    SageMakerHFEndpointConstruct,
)
from constructs import Construct


class HuggingfaceSagemakerStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment: Environment,
        gpu_count: int,
        huggingface_token_id: str,
        huggingface_model_id: str = "meta-llama/Llama-2-13b-chat-hf",
        huggingface_task: str = "text-generation",
        instance_type: str = "ml.g5.12xlarge",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        execution_role = iam.Role(
            self,
            "hf_sagemaker_exec_role",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )

        sm_exec_policy = iam.Policy(
            self,
            "sm-exec-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "sagemaker:*",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetAuthorizationToken",
                        "cloudwatch:PutMetricData",
                        "cloudwatch:GetMetricData",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:DescribeLogStreams",
                        "logs:PutLogEvents",
                        "logs:GetLogEvents",
                        "s3:CreateBucket",
                        "s3:ListBucket",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:PutObject",
                    ],
                    resources=["*"],
                )
            ],
        )

        execution_role.attach_inline_policy(sm_exec_policy)
        execution_role_arn = execution_role.role_arn

        # ToDo: Taha: Parameterize properly like e.g. variant_weight
        self.endpoint = SageMakerHFEndpointConstruct(
            self,
            "SagemakerEndpoint",
            model_name=huggingface_model_id,
            huggingface_task=huggingface_task,
            huggingface_token_id=huggingface_token_id,
            huggingface_model_region=str(environment.region),
            role_arn=execution_role_arn,
            instance_type=instance_type,
            gpu_count=gpu_count,
            instance_count=1,
            variant_weight=1,
            **kwargs,
        )

        self.endpoint.node.add_dependency(sm_exec_policy)

        model_name = huggingface_model.split("/")[-1]
        ssm.StringParameter(
            self,
            "sm_endpoint",
            parameter_name=f"/env/dev/sagemaker/{model_name}",
            string_value=self.endpoint.endpoint_name,
        )

    @property
    def sm_endpoint(self) -> SageMakerHFEndpointConstruct:
        return self.endpoint
