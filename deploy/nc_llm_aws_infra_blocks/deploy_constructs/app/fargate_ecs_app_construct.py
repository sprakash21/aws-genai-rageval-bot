import aws_cdk
from aws_cdk import SecretValue
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager, aws_ssm
from constructs import Construct
from nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct


class EcsWithLoadBalancer(BaseConstruct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        vcpus: int,
        container_memory: int,
        application_name: str,
        ecr_repository_name: str,
        ecr_image_tag: str,
        ecr_url: str,
        sagemaker_endpoint_name: aws_ssm.CfnParameter,
        openai_api_key: str,
        use_bedrock: bool,
        db_secret: aws_secretsmanager.ISecret,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create ECS Fargate Cluster
        self.cluster = ecs.Cluster(self, "ecs-fargate-cluster", vpc=vpc)

        # Create Internet Facing Load Balancer
        self.lb = elbv2.ApplicationLoadBalancer(
            self, "internet-facing-lb", vpc=vpc, internet_facing=True
        )

        # Create an S3 Bucket using cdk
        bucket_name = f"{self.resource_prefix}-bucket"

        bucket = s3.Bucket(
            self,
            bucket_name,
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=aws_cdk.RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )

        # Create a Fargate task definition
        task_def = ecs.FargateTaskDefinition(
            self,
            "fargate-task-definition",
            cpu=vcpus,
            memory_limit_mib=container_memory,
        )

        secret_name = f"{self.project_stage_prefix}-open-ai-key"
        secret = aws_secretsmanager.Secret(
            self,
            id="open-ai-key",
            secret_name=secret_name,
            secret_string_value=SecretValue.unsafe_plain_text(openai_api_key),
        )

        secret.grant_read(task_def.task_role)

        db_secret.grant_read(task_def.task_role)

        task_def.add_container(
            "fargate-app-container",
            image=ecs.ContainerImage.from_registry(
                f"{ecr_url}/{ecr_repository_name}:{ecr_image_tag}"
            ),
            memory_limit_mib=container_memory,
            cpu=vcpus,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f"{self.resource_prefix}-app-container-logs"
            ),
            port_mappings=[ecs.PortMapping(container_port=8501)],
            environment={
                "SG_ENDPOINT_NAME": sagemaker_endpoint_name.name,
                "RDS_SECRET_NAME": db_secret.secret_name,
                "OPENAI_API_KEY_NAME": secret_name,
                "BUCKET_NAME": bucket_name,
                "USE_BEDROCK": str(use_bedrock),
                "IS_DB_LOCAL": "False",
            },
        )

        policy_execution = aws_iam.Policy(
            self,
            "fargate-execution-policy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetAuthorizationToken",
                    ],
                    resources=["*"],
                ),
            ],
        )

        policy_task = aws_iam.Policy(
            self,
            "fargate-task-policy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "s3:ListBucket",
                        "s3:GetObject",
                        "s3:PutObject",
                    ],
                    resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"],
                ),
                aws_iam.PolicyStatement(
                    actions=[
                        "sagemaker:*",
                    ],
                    resources=[f"*"],
                ),
                aws_iam.PolicyStatement(
                    actions=[
                        "ssm:GetParameter",
                    ],
                    resources=[
                        f"arn:aws:ssm:{self.deploy_region}:*:parameter{sagemaker_endpoint_name.name}"
                    ],
                ),
            ],
        )

        task_def.task_role.attach_inline_policy(policy_task)
        task_def.obtain_execution_role().attach_inline_policy(policy_execution)

        # Here you might want to add a container to the task definition
        # Add listener to Load Balancer
        listener = self.lb.add_listener("listener", port=80)
        # Create Fargate Service
        fargate_service = ecs.FargateService(
            self,
            "fargate-service",
            cluster=self.cluster,
            task_definition=task_def,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )

        # Attach the service to the ALB
        listener.add_targets(
            "ecs-targets",
            port=8501,
            targets=[fargate_service],
            protocol=elbv2.ApplicationProtocol.HTTP,
        )
