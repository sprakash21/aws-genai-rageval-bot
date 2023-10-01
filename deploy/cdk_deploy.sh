#!/bin/bash

function setup(){
    local task=$1
    local aws_profile=$2
    cdk "$task" --profile "$aws_profile" --all
    exit $?
}

export TASK=$1
export AWS_PROFILE=$2

cdk_deploy "$1" "$2"