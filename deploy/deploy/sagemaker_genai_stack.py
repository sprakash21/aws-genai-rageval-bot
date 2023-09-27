from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)


class SageMakerGenAiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        