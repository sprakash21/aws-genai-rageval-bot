from email.utils import encode_rfc2231
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
)

from constructs import Construct


class EcsWithLoadBalancer(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.IVpc,
        vcpus: int,
        container_memory: int,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create ECS Fargate Cluster
        self.cluster = ecs.Cluster(self, "ecs-fargate-cluster", vpc=vpc)

        # Create Internet Facing Load Balancer
        self.lb = elbv2.ApplicationLoadBalancer(
            self, "internet-facing-lb", vpc=vpc, internet_facing=True
        )

        # Add listener to Load Balancer
        listener = self.lb.add_listener("listener", port=80)

        # Create a Fargate task definition
        task_def = ecs.FargateTaskDefinition(
            self,
            "fargate-task-definition",
            cpu=vcpus,
            memory_limit_mib=container_memory,
        )

        task_def.add_container(
            "fargate-app-container",
            image=ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample"),
            memory_limit_mib=container_memory,
            cpu=vcpus,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs-fargate-sample-app"),
        )

        # Here you might want to add a container to the task definition

        # Create Fargate Service
        fargate_service = ecs.FargateService(
            self,
            "fargate-service",
            cluster=self.cluster,
            task_definition=task_def,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ),
        )

        # Attach the service to the ALB
        listener.add_targets("ecs-targets", port=80, targets=[fargate_service])
