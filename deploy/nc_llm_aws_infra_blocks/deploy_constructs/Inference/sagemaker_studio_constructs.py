import os.path as path
import typing

from aws_cdk import aws_iam as iam

import aws_cdk.cloudformation_include as cfn_inc

from constructs import Construct


class SagemakerStudioDomainConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        sagemaker_domain_name: str,
        vpc_id: str,
        subnet_ids: typing.List[str],
        role_sagemaker_studio_users: iam.IRole,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id)

        my_sagemaker_domain = cfn_inc.CfnInclude(
            self,
            construct_id,
            template_file=path.join(
                path.dirname(path.abspath(__file__)),
                "sagemakerCfnTemplates/domain_template.yaml",
            ),
            parameters={
                "auth_mode": "IAM",
                "domain_name": sagemaker_domain_name,
                "vpc_id": vpc_id,
                "subnet_ids": subnet_ids,
                "default_execution_role_user": role_sagemaker_studio_users.role_arn,
            },
        )
        self.sagemaker_domain_id = my_sagemaker_domain.get_resource(
            "SagemakerDomainCDK"
        ).ref


class SagemakerStudioUserConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        sagemaker_domain_id: str,
        user_profile_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id)

        my_sagemaker_studio_user_template = cfn_inc.CfnInclude(
            self,
            construct_id,
            template_file=path.join(
                path.dirname(path.abspath(__file__)),
                "sagemakerCfnTemplates/user_template.yaml",
            ),
            parameters={
                "sagemaker_domain_id": sagemaker_domain_id,
                "user_profile_name": user_profile_name,
            },
            preserve_logical_ids=False,
        )
        self.user_profile_arn = (
            my_sagemaker_studio_user_template.get_resource("SagemakerUser")
            .get_att("UserProfileArn")
            .to_string()
        )
