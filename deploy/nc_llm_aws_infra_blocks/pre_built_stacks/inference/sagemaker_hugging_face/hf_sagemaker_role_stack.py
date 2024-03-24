# Adapted from Huggingface documentation.
# WIP..

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from constructs import Construct
from nc_llm_aws_infra_blocks.library.base.base_enum import BaseEnum


# an enum class representing huggingface task types
class HuggingFaceTaskType(BaseEnum):
    TextGeneration = "text-generation"


# ToDo: Taha: Append project names
class HuggingFaceSageMakerRoleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        execution_role = iam.Role(
            self,
            "sagemaker-huggingface-execution-role",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )

        self.sm_exec_policy = iam.Policy(
            self,
            "sagemaker-huggingface-execution-policy",
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

        execution_role.attach_inline_policy(self.sm_exec_policy)
        execution_role_arn = execution_role.role_arn
        self._execution_role_arn = execution_role_arn

    @property
    def execution_role_arn(self) -> str:
        return self._execution_role_arn
