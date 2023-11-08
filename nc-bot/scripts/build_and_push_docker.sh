#!/bin/bash

# Parameters
DOCKERFILE_PATH=$1
REPO_NAME=$2
IMAGE_TAG=$3
REGION=$4
ACCOUNT_ID=$5

# Functions for text coloring
color_red() {
    echo -e "\033[31m$1\033[0m"
}

color_blue() {
    echo -e "\033[34m$1\033[0m"
}

color_green() {
    echo -e "\033[32m$1\033[0m"
}

# Check if parameters are provided
if [ -z "$DOCKERFILE_PATH" ] || [ -z "$REPO_NAME" ] || [ -z "$IMAGE_TAG" ] || [ -z "$REGION" ] || [ -z "$ACCOUNT_ID" ]; then
    color_red "Error: Missing parameters."
    echo "Usage: $0 <DOCKERFILE_PATH> <REPO_NAME> <IMAGE_TAG> <REGION> <ACCOUNT_ID>"
    exit 1
fi

color_blue "Logging into ECR..."
# Get the ECR login password
response=$(aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com)

if [ "$response" == "Login Succeeded" ]
then
    aws ecr create-repository --repository-name $REPO_NAME --region $REGION

    color_blue "Building Docker image: $REPO_NAME from Dockerfile: $DOCKERFILE_PATH"
    # Build the Docker image
    docker build --platform linux/amd64 -t $REPO_NAME -f $DOCKERFILE_PATH ../
    color_blue "Tagging Docker image as: $REPO_NAME:$IMAGE_TAG"
    # Tag the image for ECR
    docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

    color_blue "Pushing Docker image to ECR repository: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
    # Push the image to ECR
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
    color_green "Process completed successfully!"

    # Output all created values
    echo -e "\n\033[1mCreated Values:\033[0m"
    echo "Repository Name: $REPO_NAME"
    echo "Image Tag: $IMAGE_TAG"
    echo "AWS Region: $REGION"
    echo "Account ID: $ACCOUNT_ID"
    echo "Full Image URL: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"
else
    echo "Could not login to aws ecr. Check if the variables passed are correct"
fi