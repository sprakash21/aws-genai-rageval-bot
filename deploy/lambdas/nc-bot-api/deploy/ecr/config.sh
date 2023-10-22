#!/bin/bash
export PROFILE=nc-admin
ACCOUNT_ID=$(aws sts get-caller-identity --profile ${PROFILE} --query "Account" --output text)
export ACCOUNT_ID
export REGION=eu-central-1
export TAG=latest
# Name should match to the infrastructure created.
export ECR_REPO=gen-ai/nc-bot-api
