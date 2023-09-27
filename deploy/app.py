#!/usr/bin/env python3

import aws_cdk as cdk

from deploy.sagemaker_studio_stack import SagemakerStudioStack
from deploy.network_stack import VPCNetworkStack


app = cdk.App()
network_stack = VPCNetworkStack(app, "VPCNetworkStack")
SagemakerStudioStack(app, "deploy", vpc=network_stack.vpc)

app.synth()
