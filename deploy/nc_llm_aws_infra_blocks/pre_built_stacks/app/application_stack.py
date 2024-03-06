from typing import Union

from aws_cdk import CfnParameter, Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from nc_llm_aws_infra_blocks.deploy_constructs.app.aurora_postgres_sl_context_db_construct import (
    AuroraPostgresSlContextDb,
)
from nc_llm_aws_infra_blocks.deploy_constructs.app.fargate_ecs_app_construct import (
    EcsWithLoadBalancer,
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
        application_name: str,
        ecr_repository_name: str,
        ecr_image_tag: str,
        ecr_url: str,
        app_params: dict[str, str],
        container_vcpus: Union[int, float],
        container_memory: int,
        domain_name: Union[str, None] = None,
        hosted_zone_id: Union[str, None] = None,
        sagemaker_endpoint_name: Union[CfnParameter, None] = None,
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

        app_ecr_stack = EcsWithLoadBalancer(
            self,
            "ecs-app",
            vpc=vpc,
            vcpus=container_vcpus,
            container_memory=container_memory,
            application_name=application_name,
            ecr_repository_name=ecr_repository_name,
            ecr_image_tag=ecr_image_tag,
            ecr_url=ecr_url,
            project_prefix=project_prefix,
            deploy_stage=deploy_stage,
            deploy_region=deploy_region,
            sagemaker_endpoint_name=sagemaker_endpoint_name,
            app_params=app_params,
            db_secret=context_db.db_secret,
            domain_name=domain_name,
            hosted_zone_id=hosted_zone_id,
        )
