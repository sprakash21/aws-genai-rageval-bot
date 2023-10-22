from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct


class DeveloperStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._key_pair = ec2.CfnKeyPair(
            self,
            "dev-ssh-key",
            key_name="dev-ssh-key",
        )
        self._machine_image = ec2.MachineImage.from_ssm_parameter(
            "/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id",
            os=ec2.OperatingSystemType.LINUX,
        )
        self._dev_sg = ec2.SecurityGroup(self, "dev-sg", vpc=vpc)
        self._dev_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(8501), "Streamlit access"
        )
        self._dev_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "ssh access"
        )
        self.dev_instance = ec2.Instance(
            self,
            "dev-machine",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=self._dev_sg,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.M5, ec2.InstanceSize.XLARGE
            ),
            machine_image=self._machine_image,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1", volume=ec2.BlockDeviceVolume.ebs(100)
                )
            ],
            key_name=self._key_pair.key_name
        )
