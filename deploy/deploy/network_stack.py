from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct


class VPCNetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.output_vpc = ec2.Vpc(self, "VPC",
            vpc_name="nc-genai-vpc",
            nat_gateways=1,
            cidr="10.0.0.0/16",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC,cidr_mask=24),
                ec2.SubnetConfiguration(name="private",subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,cidr_mask=24)
            ]
        )

    @property
    def vpc(self) -> ec2.Vpc:
        return self.output_vpc