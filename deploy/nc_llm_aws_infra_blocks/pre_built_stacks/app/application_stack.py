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
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        context_db = AuroraPostgresSlContextDb(
            self,
            "eh-context",
            vpc=vpc,
            deploy_region=deploy_region,
            project_prefix=project_prefix,
            deploy_stage=deploy_stage,
        )
