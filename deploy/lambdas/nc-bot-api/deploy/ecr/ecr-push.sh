#!/bin/bash
ecr_push(){
    # The built image id is automatically fetched by filtering on image_name reference. 
    image_id=$(docker images --filter=reference='*/mask-service:latest' --format='{{.ID}}')
    if [ -z "$image_id" ] || [ -z "${ACCOUNT_ID}" ]
    then
        echo "(image_id, account_id) are mandatory parameters for execution and cannot be empty. Exiting..."
        exit 1
    elif [ -z "${TAG}" ]
    then
        echo "Tag is not passed. Assuming it to be latest.."
        TAG=latest
    elif [ -z "${REGION}" ]
    then
        echo "region is not passed assuming default to eu-central-1"
        REGION=eu-central-1
    fi

    account_info="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

    rc=$(aws ecr get-login-password --region "${REGION}" --profile "${PROFILE}" | docker login --username AWS --password-stdin "$account_info")

    if [ "$rc" == "Login Succeeded" ]
    then
        # Create the repository if it does not already exists.
        # Double pipe (||) here means if non-zero from previous one then only next command is executed.
        aws ecr describe-repositories --repository-names "${ECR_REPO}" --region "${REGION}" --profile "${PROFILE}" || aws ecr create-repository --repository-name "${ECR_REPO}" --region "${REGION}" --profile "${PROFILE}"
        
        # Tag and push it to ECR
        docker tag "$image_id" "$account_info"/"${ECR_REPO}":"${TAG}"
        docker push "$account_info"/"${ECR_REPO}":"${TAG}"
        echo "The push to AWS is completed"
    else
        # Exit
        echo "The specified arguments were not correct. Could not login"
    fi
}

ecr_push "$@"
