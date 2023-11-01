from aws_cdk import aws_rds as rds, Stack, aws_ec2 as ec2
from constructs import Construct


class DBStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._db_sg = ec2.SecurityGroup(self, "db-sg", vpc=vpc)
        self._db_sg.add_ingress_rule(
            ec2.Peer.ipv4("10.0.0.0/16"),
            ec2.Port.tcp(5432),
            "Ec2 connecting to RDS",
        )
        self.instance = rds.DatabaseInstance(
            self,
            "Instance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
            ),
            # Does not work by updating stack. Best create secret separate and pass it.
            credentials=rds.Credentials.from_generated_secret(
                "postgres",
                secret_name="env/dev/rds_postgres",
                exclude_characters="`\"$%'!&*^#@()}{[]\\>=+<?%/",
            ),
            vpc=vpc,
            # TODO: Change to private when all functionality on aws
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            ca_certificate=rds.CaCertificate.RDS_CA_RDS2048_G1,
            max_allocated_storage=200,
            cloudwatch_logs_exports=["postgresql"],
            # Set true if prod
            multi_az=False,
            publicly_accessible=True,
            database_name="vectordblab",
        )

    @property
    def db_secret(self):
        return self.instance.secret
