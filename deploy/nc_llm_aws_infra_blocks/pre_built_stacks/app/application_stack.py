from aws_cdk import (
    Duration,
    Size,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct

from nc_llm_aws_infra_blocks.deploy_constructs.app.aurora_postgres_sl_context_db_construct import (
    AuroraPostgresSlContextDb,
)


class SimpleRagAppStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        context_db = AuroraPostgresSlContextDb(
            self,
            "context-db",
            vpc=vpc,
        )

        # # Defines role for the AWS Lambda functions
        # role = iam.Role(
        #     self,
        #     "AWS-Lambda-Policy",
        #     assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        # )
        # role.add_managed_policy(
        #     iam.ManagedPolicy.from_aws_managed_policy_name(
        #         "service-role/AWSLambdaBasicExecutionRole"
        #     )
        # )
        # role.add_managed_policy(
        #     iam.ManagedPolicy.from_aws_managed_policy_name(
        #         "service-role/AWSLambdaVPCAccessExecutionRole"
        #     )
        # )
        # role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "sm-invoke-policy",
        #         statements=[
        #             iam.PolicyStatement(
        #                 effect=iam.Effect.ALLOW,
        #                 actions=["sagemaker:InvokeEndpoint"],
        #                 resources=["*"],
        #             )
        #         ],
        #     )
        # )
        # role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "s3-policy",
        #         statements=[
        #             iam.PolicyStatement(
        #                 effect=iam.Effect.ALLOW,
        #                 actions=["s3:*"],
        #                 resources=["arn:aws:s3:::lambda-tests-132111/*"],
        #             )
        #         ],
        #     )
        # )

        # role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "secrets-policy",
        #         statements=[
        #             iam.PolicyStatement(
        #                 effect=iam.Effect.ALLOW,
        #                 actions=[
        #                     "secretsmanager:GetResourcePolicy",
        #                     "secretsmanager:GetSecretValue",
        #                     "secretsmanager:DescribeSecret",
        #                     "secretsmanager:ListSecretVersionIds",
        #                 ],
        #                 resources=["*"],
        #             )
        #         ],
        #     )
        # )
        # role.attach_inline_policy(
        #     iam.Policy(
        #         self,
        #         "other-policy",
        #         statements=[
        #             iam.PolicyStatement(
        #                 effect=iam.Effect.ALLOW,
        #                 actions=[
        #                     "cloudwatch:PutMetricData",
        #                     "cloudwatch:GetMetricData",
        #                     "cloudwatch:GetMetricStatistics",
        #                     "cloudwatch:ListMetrics",
        #                     "logs:CreateLogGroup",
        #                     "logs:CreateLogStream",
        #                     "logs:DescribeLogStreams",
        #                     "logs:PutLogEvents",
        #                     "logs:GetLogEvents",
        #                 ],
        #                 resources=["*"],
        #             )
        #         ],
        #     )
        # )
        # self.uploader_lambda = _lambda.DockerImageFunction(
        #     scope=self,
        #     id="upload-vectordb",
        #     role=role,
        #     # Function name on AWS
        #     function_name="uploadToVectorDB",
        #     # Use aws_cdk.aws_lambda.DockerImageCode.from_image_asset to build
        #     # a docker image on deployment
        #     code=_lambda.DockerImageCode.from_image_asset(
        #         # Directory relative to where you execute cdk deploy
        #         # contains a Dockerfile with build instructions
        #         directory="lambdas/nc-bot-api",
        #         cmd=["data_upload.lambda_handler"],
        #     ),
        #     architecture=_lambda.Architecture.ARM_64,
        #     ephemeral_storage_size=Size.gibibytes(10),
        #     memory_size=10000,
        #     timeout=Duration.minutes(15),
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        #     ),
        #     vpc=vpc,
        # )
