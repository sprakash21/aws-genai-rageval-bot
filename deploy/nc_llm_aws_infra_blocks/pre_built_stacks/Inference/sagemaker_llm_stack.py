from constructs import Construct
from aws_cdk import Stack, aws_iam as iam, aws_ssm as ssm, aws_sagemaker as sagemaker


from nc_llm_aws_infra_blocks.deploy_constructs.Inference.sagemaker_endpoint_construct import (
    SageMakerEndpointConstruct,
)


class SageMakerLLMStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, model_info, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        role = iam.Role(
            self,
            "llm-sagemaker-policy",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        sts_policy = iam.Policy(
            self,
            "sm-sts-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW, actions=["sts:AssumeRole"], resources=["*"]
                )
            ],
        )

        logs_policy = iam.Policy(
            self,
            "sm-logs-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudwatch:PutMetricData",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:CreateLogGroup",
                        "logs:DescribeLogStreams",
                        "ecr:GetAuthorizationToken",
                    ],
                    resources=["*"],
                )
            ],
        )

        ecr_policy = iam.Policy(
            self,
            "sm-ecr-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ecr:*",
                    ],
                    resources=["*"],
                )
            ],
        )

        role.attach_inline_policy(sts_policy)
        role.attach_inline_policy(logs_policy)
        role.attach_inline_policy(ecr_policy)

        self.endpoint = SageMakerEndpointConstruct(
            self,
            "llm_textgeneration",
            project_prefix="GenAI-Demo",
            role_arn=role.role_arn,
            model_name="meta-textgen-stack",
            model_bucket_name=model_info["model_bucket_name"],
            model_bucket_key=model_info["model_bucket_key"],
            model_docker_image=model_info["model_docker_image"],
            variant_name="AllTraffic",
            variant_weight=1,
            instance_count=1,
            instance_type=model_info["instance_type"],
            environment={
                "SAGEMAKER_ENV": "1",
                "SAGEMAKER_MODEL_SERVER_TIMEOUT": "3600",
                "SAGEMAKER_MODEL_SERVER_WORKERS": "1",
                "SAGEMAKER_REGION": model_info["region_name"],
            },
            deploy_enable=True,
        )

        self.endpoint.node.add_dependency(sts_policy)
        self.endpoint.node.add_dependency(logs_policy)
        self.endpoint.node.add_dependency(ecr_policy)

        ssm.StringParameter(
            self,
            "sm_endpoint",
            parameter_name="sm_endpoint",
            string_value=self.endpoint.endpoint_name,
        )

    @property
    def sm_endpoint(self) -> sagemaker.CfnEndpoint:
        return self.endpoint
