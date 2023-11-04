# Adapted from Huggingface documentation.
# WIP..
from aws_cdk import aws_iam as iam, aws_ssm as ssm, aws_sagemaker as sagemaker, Stack
from deploy_constructs.sagemaker_endpoint_construct import SageMakerHFEndpointConstruct
from constructs import Construct


class HuggingfaceSagemakerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Context parameters
        huggingface_model = (
            self.node.try_get_context("model") or "meta-llama/Llama-2-7b-chat-hf"
        )
        # cdk context vars
        huggingface_task = self.node.try_get_context("task") or "text-generation"
        instance_type = self.node.try_get_context("instance_type") or "ml.g5.2xlarge"
        huggingface_token_id = self.node.try_get_context("hf_id") or ""

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

        self.endpoint = SageMakerHFEndpointConstruct(
            self,
            "SagemakerEndpoint",
            huggingface_model=huggingface_model,
            huggingface_task=huggingface_task,
            huggingface_token_id=huggingface_token_id,
            execution_role_arn=execution_role_arn,
            instance_type=instance_type,
            **kwargs
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
    def sm_endpoint(self) -> sagemaker.CfnEndpoint:
        return self.endpoint
