from aws_cdk import (
    Duration,
    aws_rds as rds,
    Stack,
    aws_ec2 as ec2,
    SecretsManagerSecretOptions,
)
from aws_cdk.aws_rds import (
    ServerlessCluster,
    DatabaseClusterEngine,
    AuroraPostgresEngineVersion,
    ServerlessScalingOptions,
)
from constructs import Construct
from nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct


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

        # Aurora Serverless cluster
        self.cluster = ServerlessCluster(
            self,
            f"{self.resource_prefix}-db",
            engine=DatabaseClusterEngine.aurora_postgres(
                version=AuroraPostgresEngineVersion.VER_13_4
            ),
            vpc=vpc,
            security_groups=[self._db_sg],
            scaling=ServerlessScalingOptions(
                auto_pause=Duration.minutes(10),
                min_capacity=rds.AuroraCapacityUnit.ACU_2,
                max_capacity=rds.AuroraCapacityUnit.ACU_8,
            ),
            default_database_name="context_db",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            credentials=self.credentials,
        )

    @property
    def db_secret_name(self) -> str:
        return self.secret_name

    @property
    def db_secret(self):
        return self.cluster.secret
