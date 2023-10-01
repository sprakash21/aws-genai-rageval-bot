#!/bin/bash

function setup(){
    local task=$1
    local aws_profile=$2
    if [[ "$task" == "synth" ]]; then
        echo "Synthethizing the CDK template"
        cdk "$task" --profile "$aws_profile" --all
    elif [[ "$task" == "deploy" ]]; then
        echo "Deploying the stack to AWS..."
        cdk "$task" --profile "$aws_profile" --all
    elif [[ "$task" == "destroy" ]]; then
        echo "Destroying the stack to AWS..."
        cdk "$task" --profile "$aws_profile" --all
    else
        echo "The task is not defined. Only supported are synth, deploy and destroy"
    fi
    exit $?
}

export TASK=$1
export AWS_PROFILE=$2

setup "$1" "$2"