from constructs import Construct
from aws_cdk import Stack, aws_ec2 as ec2, aws_iam as iam, CfnOutput

from deploy_constructs.sagemaker_studio_constructs import (
    SagemakerStudioDomainConstruct,
    SagemakerStudioUserConstruct,
)


class SagemakerStudioStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        role_sagemaker_studio_domain = iam.Role(
            self,
            "RoleForSagemakerStudioUsers",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            role_name="RoleSagemakerStudioUsers",
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    self,
                    id="SagemakerReadAccess",
                    managed_policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                )
            ],
        )
        self.role_sagemaker_studio_domain = role_sagemaker_studio_domain
        self.sagemaker_domain_name = "DomainForSagemakerStudio"
        self.vpc_id = vpc.vpc_id
        self.public_subnet_ids = [
            public_subnet.subnet_id for public_subnet in vpc.public_subnets
        ]
        my_sagemaker_domain = SagemakerStudioDomainConstruct(
            self,
            "mySagemakerStudioDomain",
            sagemaker_domain_name=self.sagemaker_domain_name,
            vpc_id=self.vpc_id,
            subnet_ids=self.public_subnet_ids,
            role_sagemaker_studio_users=self.role_sagemaker_studio_domain,
        )
        # For more teams iterate this.
        my_default_datascience_user = SagemakerStudioUserConstruct(
            self,
            "dsc-1",
            sagemaker_domain_id=my_sagemaker_domain.sagemaker_domain_id,
            user_profile_name="dsc-1",
        )
        CfnOutput(
            self,
            f"cfnoutput-dsc-1",
            value=my_default_datascience_user.user_profile_arn,
            description="The User Arn TeamA domain ID",
            export_name=f"UserArn-dsc-1",
        )
        CfnOutput(
            self,
            "DomainIdSagemaker",
            value=my_sagemaker_domain.sagemaker_domain_id,
            description="The sagemaker domain ID",
            export_name="DomainIdSagemaker",
        )
