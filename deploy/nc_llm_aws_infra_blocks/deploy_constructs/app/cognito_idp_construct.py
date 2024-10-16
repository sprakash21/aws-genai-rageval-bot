import string

import cdk_nag
from aws_cdk import (
    aws_cognito as cognito,
    aws_secretsmanager as secretsmanager,
    aws_lambda as _lambda,
    aws_iam as iam,
    custom_resources as cr,
    CfnOutput, SecretValue, Stack, Aws, CustomResource, Aspects, Duration
)
from constructs import Construct

from nc_llm_aws_infra_blocks.library.base.base_construct import BaseConstruct
import secrets


def _generate_password(length=12):
    # Define password character requirements
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Securely generate a random password
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))

        # Ensure password meets requirements: at least one uppercase, lowercase, digit, and special character
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            break

    return password


class CognitoStack(BaseConstruct):
    """
    Deploys the Cognito-Idp to AWS account and reference user for login to application
    """

    def __init__(self,
                 scope: Construct,
                 id: str,
                 account: str,
                 app_params: dict[str, str],
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Step 1: Create the Cognito User Pool
        self.user_pool = cognito.UserPool(
            self, f"RagTrackUserPool-{self.deploy_stage}",
            self_sign_up_enabled=False,  # Admins create users
            sign_in_aliases=cognito.SignInAliases(username=True),  # Users sign in using username
            auto_verify=cognito.AutoVerifiedAttrs(email=False, phone=False),
            password_policy=cognito.PasswordPolicy(
                min_length=8,                   # Minimum length of 8 characters
                require_lowercase=True,          # Require lowercase letters
                require_uppercase=True,          # Require uppercase letters
                require_digits=True,             # Require at least one number
                require_symbols=True             # Require at least one special character
            ),
            advanced_security_mode=cognito.AdvancedSecurityMode.ENFORCED,
            mfa=cognito.Mfa.OPTIONAL  # Optional MFA
        )

        # Step 2: Create an App Client for the User Pool
        self.app_client = self.user_pool.add_client(
            f"RagTrackAppClient-{self.deploy_stage}",
            auth_flows=cognito.AuthFlow(
                user_password=True  # Enable USER_PASSWORD_AUTH flow
            ),
            generate_secret=True,  # Generate a client secret for this app
        )

        # Create client secret information
        client_secret = {
            "client_id": SecretValue.unsafe_plain_text(self.app_client.user_pool_client_id),
            "client_secret": self.app_client.user_pool_client_secret
        }
        self.client_secret_info = secretsmanager.Secret(
            self, f"RagTrackUserPasswordSecret-{self.deploy_stage}",
            secret_name=f"/env/dev/cognito_app_client",
            secret_object_value=client_secret,
        )

        # Define a custom IAM policy for Cognito interactions (optional, based on secret use case)
        cognito_rotation_policy = iam.PolicyStatement(
            actions=[
                "cognito-idp:AdminSetUserPassword",
                "cognito-idp:AdminUpdateUserAttributes",
                "cognito-idp:ListUsers"
            ],
            resources=[self.user_pool.user_pool_arn],  # You can restrict this to specific Cognito pools if necessary
        )

        # Create a role for the Secrets Manager rotation Lambda
        rotation_lambda_role = iam.Role(
            self, "CustomRotationLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Attach the policies to the role
        rotation_lambda_role.add_to_policy(cognito_rotation_policy)

        # Step 4: Create a User (Without Password)

        self.user = cognito.CfnUserPoolUser(
            self, f"RagTrackUser-{self.deploy_stage}",
            user_pool_id=self.user_pool.user_pool_id,
            username=app_params["COGNITO_USERNAME"],
            user_attributes=[{
                'name': 'email',
                'value': app_params["COGNITO_EMAIL"]
            }]
        )

        # Step 5: Create Lambda function to set the password
        random_password = _generate_password(length=10)
        password_lambda = _lambda.Function(
            self, f"SetUserPasswordFunction-{self.deploy_stage}",
            runtime=_lambda.Runtime.PYTHON_3_12,
            role=rotation_lambda_role,
            handler="set_password.handler",
            code=_lambda.Code.from_inline(
                """
import boto3
import os

client = boto3.client('cognito-idp')

def handler(event, context):
    user_pool_id = os.environ['USER_POOL_ID']
    username = os.environ['COGNITO_USERNAME']
    password = os.environ['COGNITO_PASSWORD']

    # Set user password
    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=password,
        Permanent=True  # Makes the password permanent
    )

    return {"status": "password set successfully"}
                """
            ),
            environment={
                'USER_POOL_ID': self.user_pool.user_pool_id,
                'COGNITO_USERNAME': app_params["COGNITO_USERNAME"],
                'COGNITO_PASSWORD': random_password
            }
        )


        # Step 6: Custom Resource to trigger the Lambda after user creation
        # password_custom_resource = cr.Provider(
        #      self,
        #      f"PasswordCustomResourceProvider-{self.deploy_stage}",
        #      on_event_handler=password_lambda,
        #      role=rotation_lambda_role
        # )
        #
        # CustomResource(
        #      self, f"SetPasswordCustomResource-{self.deploy_stage}",
        #      service_token=password_custom_resource.service_token
        # )
        #
        # # Step 7: Store the Username and Password in Secrets Manager
        # secret_user_secret = {
        #     "username": SecretValue.unsafe_plain_text(app_params['COGNITO_USERNAME']),
        #     "password": SecretValue.unsafe_plain_text(random_password)
        # }
        # self.user_secret = secretsmanager.Secret(
        #     self, f"RagTrackUserPasswordSecret-{self.deploy_stage}",
        #     secret_name=f"/env/dev/cognito_user_details_1",
        #     secret_object_value=secret_user_secret,
        # )
        # # Is only a placeholder for rotation
        # self.user_secret.add_rotation_schedule("RotationScheduleCognitoIdpSecret",
        #                                   rotation_lambda=_lambda.Function(
        #                                       self, "UserPasswordRotationLambda",
        #                                       runtime=_lambda.Runtime.PYTHON_3_12,
        #                                       role=rotation_lambda_role,
        #                                       handler="rotate_user_password.handler",
        #                                       code=_lambda.Code.from_inline(
        #                                           """
        #                                           import boto3
        #                                           import os
        #                                           def handler(event, context):
        #                                               # Implement logic for user password rotation
        #                                               print("Password rotation logic is not implemented yet.")
        #                                           """
        #                                       ),
        #                                   ),
        #                                   automatically_after=Duration.days(30)
        #                                   )

        # Step 8: Output the secret IDs and client information
        # CfnOutput(
        #     self, f"RagTrackUserPasswordSecretID-{self.deploy_stage}",
        #     value=self.user_secret.secret_arn,
        #     description="The ARN of the Secret storing the user credentials"
        # )

        CfnOutput(
            self, f"RagTrackUserPoolID-{self.deploy_stage}",
            value=self.user_pool.user_pool_id,
            description="The User Pool ID"
        )

        CfnOutput(
            self, f"RagTrackAppClientID-{self.deploy_stage}",
            value=self.app_client.user_pool_client_id,
            description="The App Client ID"
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks(verbose=True))

    @property
    def client_secret_name(self):
        return self.client_secret_info.secret_name

    @property
    def client_secret_arn(self):
        return self.client_secret_info.secret_arn

    @property
    def client_secret(self):
        return self.client_secret_info