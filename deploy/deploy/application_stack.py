from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct


class AppStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, endpoint, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Defines role for the AWS Lambda functions
        role = iam.Role(
            self,
            "AWS-Lambda-Policy",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaVPCAccessExecutionRole"
            )
        )
        role.attach_inline_policy(
            iam.Policy(
                self,
                "sm-invoke-policy",
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["sagemaker:InvokeEndpoint"],
                        resources=["*"],
                    )
                ],
            )
        )

        # Defines an AWS Lambda function for code llama
        lambda_code_llama = _lambda.Function(
            self,
            "lambda_infer_fn",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambdas/code-llama"),
            handler="app_code_llama.handler",
            role=role,
            timeout=Duration.seconds(900),
            memory_size=2000,
            environment={
                "TOP_K": "50",
                "TOP_P": "0.6",
                "TEMPERATURE": "0.9",
                "MAX_NEW_TOKENS": "512",
                "REPETATION_PENALITY": "1.03",
                "SM_ENDPOINT_NAME": endpoint.endpoint_name,
            },
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ),
            vpc=vpc,
        )

        # Defines an Amazon API Gateway endpoint for Code Llama
        self.code_llama_apigw_endpoint = apigw.LambdaRestApi(
            self, "code_llama_apigw_endpoint", handler=lambda_code_llama
        )

        # Parameter Store to contain the URL
        ssm.StringParameter(
            self,
            "code_llama_sm_apigw_endpoint",
            parameter_name="code_llama_apigw_endpoint",
            string_value=self.code_llama_apigw_endpoint.url,
        )

    @property
    def apigw(self) -> apigw.LambdaRestApi.url:
        return self.code_llama_apigw_endpoint.url
