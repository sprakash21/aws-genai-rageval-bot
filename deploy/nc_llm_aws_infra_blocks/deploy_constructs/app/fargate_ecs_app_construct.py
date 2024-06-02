from typing import Union
import cdk_nag
import aws_cdk
from aws_cdk import Aws
from aws_cdk import CfnOutput, CfnParameter, SecretValue, Aspects
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager
from constructs import Construct
from nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct
from aws_cdk import aws_route53 as route53
from aws_cdk.aws_route53_targets import LoadBalancerTarget


class EcsWithLoadBalancer(BaseConstruct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        vcpus: Union[int, float],
        container_memory: int,
        application_name: str,
        ecr_repository_name: str,
        ecr_image_tag: str,
        ecr_url: str,
        sagemaker_endpoint_name: Union[CfnParameter, None],
        app_params: dict[str, str],
        db_secret: aws_secretsmanager.ISecret,
        domain_name: Union[str, None] = None,
        hosted_zone_id: Union[str, None] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        # Create ECS Fargate Cluster
        #print(self.deploy_account)
        self.cluster = ecs.Cluster(
            self, "ecs-fargate-cluster", vpc=vpc, container_insights=True
        )
        # Create Internet Facing Load Balancer
        self.lb = elbv2.ApplicationLoadBalancer(
            self, "internet-facing-lb", vpc=vpc, internet_facing=True,
        )
        # Create an S3 Bucket using cdk
        bucket_name = f"{self.resource_prefix}-{self.deploy_region}-bucket"
        #self.bucket = s3.Bucket.from_bucket_name(
        #    self, "ExstingBucket", bucket_name=bucket_name
        #)
        #if not self.bucket.bucket_name:
        self.bucket = s3.Bucket(
            self,
            bucket_name,
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED,
            auto_delete_objects=True,
            #server_access_logs_bucket=True,
            enforce_ssl=True
        )
        #else:
            #print(f"The Bucket with name - {bucket_name} exists already")
            #print(f"Bucket ARN - {self.bucket.bucket_arn}")

        # Enable access logs
        # As per: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html#attach-bucket-policy
        # There seems to be an issue with the cdk not detecting the region from the stack
        #resource_policy = aws_iam.PolicyStatement(
        #            actions=["s3:PutObject"],
        #            resources=[
        #                f"arn:aws:s3:::{bucket_name}/logs/AWSLogs/*"
        #            ],
         #           principals=[aws_iam.ArnPrincipal("arn:aws:iam:054676820928:root")]
         #       )
        # Define the bucket policy
        self.bucket.add_to_resource_policy(
            permission=aws_iam.PolicyStatement(
                actions=["s3:PutObject"],
                effect=aws_iam.Effect.ALLOW,
                resources=[self.bucket.arn_for_objects("*")],
                conditions={
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                },
                principals=[aws_iam.ServicePrincipal("delivery.logs.amazonaws.com")]
            )
        )
        # Add the resource policy for elb
        #bucket.add_to_resource_policy(permission=resource_policy)
        # Create a Fargate task definition
        task_def = ecs.FargateTaskDefinition(
            self,
            "fargate-task-definition",
            cpu=vcpus,
            memory_limit_mib=container_memory,
        )
        db_secret.grant_read(task_def.task_role)
        # Bucket work
        #self.bucket.grant_read_write(task_def.task_role)
        #self.bucket.grant_put(task_def.task_role)
        #self.bucket.grant_put_acl(task_def.task_role)
        self.lb.log_access_logs(bucket=self.bucket)

        app_env = {
            "RDS_SECRET_NAME": db_secret.secret_name,
            "BUCKET_NAME": bucket_name,
            **app_params,
        }

        if sagemaker_endpoint_name:
            app_env["SAGEMAKER_ENDPOINT_SSM_PARAM_NAME"] = str(
                sagemaker_endpoint_name.name
            )

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
            environment=app_env,
        )
        policy_execution = aws_iam.Policy(
            self,
            "fargate-execution-policy",
            statements=[
                aws_iam.PolicyStatement(
                    actions=[
                        "ecr:GetAuthorizationToken"
                    ],
                    resources=["*"],
                ),
                aws_iam.PolicyStatement(
                    actions=[
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability"
                    ],
                    resources=[
                        f"arn:aws:ecr:{self.deploy_region}:{scope.account}:repository/{ecr_repository_name}"
                    ],
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
                        "s3:DeleteObject",
                    ],
                    # Requires the bucket_arn with wildcard f"{bucket.bucket_arn}/*"
                    resources=[self.bucket.bucket_arn,f"{self.bucket.bucket_arn}/*"],
                ),
                aws_iam.PolicyStatement(
                    actions=[
                        "bedrock:GetFoundationModel",
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                    ],
                    resources=[f"arn:aws:bedrock:{app_params['BEDROCK_INFERENCE_REGION']}::foundation-model/{app_params['BEDROCK_INFERENCE_MODEL_ID']}",
                    f"arn:aws:bedrock:{app_params['BEDROCK_EVALUATION_REGION']}::foundation-model/{app_params['BEDROCK_EVALUATION_MODEL_ID']}",
                    "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v1"],
                ),
            ],
        )
        if sagemaker_endpoint_name:
            policy_task.add_statements(
                aws_iam.PolicyStatement(actions=["sagemaker:*",], resources=["*"],),
            )
            policy_task.add_statements(
                aws_iam.PolicyStatement(
                    actions=["ssm:GetParameter",],
                    resources=[
                        f"arn:aws:ssm:{self.deploy_region}:*:parameter{sagemaker_endpoint_name.name}"
                    ],
                ),
            )

        task_def.task_role.attach_inline_policy(policy_task)
        task_def.obtain_execution_role().attach_inline_policy(policy_execution)

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

        if domain_name:
            certificate = acm.Certificate(
                self,
                "Certificate",
                domain_name=f"*.{domain_name}",
                validation=acm.CertificateValidation.from_dns(),
            )
            listener = self.lb.add_listener(
                "HttpsListener", port=443, certificates=[certificate]
            )

            listener.add_targets(
                "ecs-targets",
                port=8501,
                targets=[fargate_service],
                protocol=elbv2.ApplicationProtocol.HTTP,  # Ensure this matches your service configuration
            )

            # Retrieve an existing hosted zone
            hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
                self,
                "HostedZone",
                hosted_zone_id=hosted_zone_id,
                zone_name=domain_name,
            )

            # Add a DNS A record to point to the ELB
            route53.ARecord(
                self,
                "AliasRecord",
                zone=hosted_zone,
                target=route53.RecordTarget.from_alias(LoadBalancerTarget(self.lb)),
                record_name="chat",
            )

        else:
            listener = self.lb.add_listener("listener", port=80,)

            listener.add_targets(
                "ecs-targets",
                port=8501,
                targets=[fargate_service],
                protocol=elbv2.ApplicationProtocol.HTTP,  # Ensure this matches your service configuration
            )
        # Output
        CfnOutput(
            scope=self,
            id=f"{bucket_name}-OutputARN",
            value=str(self.bucket.bucket_arn),
        )
        CfnOutput(
            scope=self,
            id=f"internet-facing-lb-DNSOutput",
            value=str(self.lb.load_balancer_dns_name),
        )
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(verbose=True))
    
    @property
    def bucket_arn(self):
        return self.bucket.bucket_arn