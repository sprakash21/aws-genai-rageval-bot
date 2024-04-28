from aws_cdk import Duration, Aspects
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as sm
from aws_cdk.aws_rds import (
    AuroraPostgresEngineVersion,
    DatabaseClusterEngine,
    ServerlessCluster,
    ServerlessScalingOptions,
    ServerlessV2ClusterInstanceProps,
)
from constructs import Construct
from nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct
import cdk_nag


class AuroraPostgresSlContextDb(BaseConstruct):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._db_sg = ec2.SecurityGroup(self, "db-sg", vpc=vpc)

        self._db_sg.add_ingress_rule(
            ec2.Peer.ipv4(vpc.vpc_cidr_block),
            ec2.Port.tcp(5432),
            "Ec2 connecting to Aurora Serverless",
        )

        self.secret_name = f"{self.resource_prefix}-db-secrets"
        self.credentials = rds.Credentials.from_generated_secret(
            "postgres",
            secret_name=self.secret_name,
            exclude_characters="`\"$%'!&*^#@()}{[]\\>=+<?%/",
        )

        self.cluster = rds.DatabaseCluster(
            self,
            f"{self.resource_prefix}-db",
            writer=rds.ClusterInstance.serverless_v2("writer"),
            readers=[
                rds.ClusterInstance.serverless_v2("reader1", scale_with_writer=True)
            ],
            vpc=vpc,
            credentials=self.credentials,
            default_database_name="context_db",
            security_groups=[self._db_sg],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            engine=DatabaseClusterEngine.aurora_postgres(
                version=AuroraPostgresEngineVersion.of("13.11", "13")
            ),
            storage_encrypted=True,
            # Disable this to allow deletion of DB
            deletion_protection=True,
        )
        #
        self.cluster.secret.add_rotation_schedule(
            "RotationSchedule",
            hosted_rotation=sm.HostedRotation.postgre_sql_single_user(
                exclude_characters="`\"$%'!&*^#@()}{[]\\>=+<?%/"
            ),
            rotate_immediately_on_update=False,
            automatically_after=Duration.days(30),
        )
        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(verbose=True))

    @property
    def db_secret_name(self) -> str:
        return self.secret_name

    @property
    def db_secret(self):
        return self.cluster.secret
