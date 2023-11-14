# RAGTrack Deployment on AWS

## Introduction

RAGTrack deployment solution is designed for flexible RAG app deployment on native AWS Services.

## Deployment Overview

The deployment of RAGTrack is executed through the AWS Cloud Development Kit (CDK), utilizing Python as the programming language. This setup ensures a streamlined deployment process.

### Key Components

The deployment uses `nc_llm_aws_infra_blocks`, a package that provides CDK constructs and stacks for a quick setup of a Retrieval Augmented Generation (RAG) application. The main stacks include Inference on SageMaker AWS Models, Inference on SageMaker Hugging Face models, the Application stack, and a VPC stack.

### Configuration Parameters

The `cdk.template.json` configuration file outlines the parameters for deployment. You can use the `cdk.template.json` as it is by adding the 2 missing values for `openai_api_key` and `huggingface.token_id`. 

Below is a detailed description of each parameter:

- `huggingface.token_id`: The token ID for Hugging Face, required for authentication and accessing Hugging Face models.

- `huggingface.llama2.13b`: Configuration settings specific to the Hugging Face 'llama2.13b' model used by the application.
  - `model_id`: The specific model identifier as recognized by Hugging Face. This ID is used to fetch the correct model.
  - `task`: The type of task for which the model is optimized, as defined by Hugging Face. This could be text generation, classification, etc.

- `inference_endpoint`: Settings for the SageMaker inference endpoint, which is the AWS service used to deploy machine learning models for inference.
  - `instance_type`: Specifies the type of instance (e.g., computational power, memory) used for the SageMaker inference endpoint. This determines the capacity and performance of the inference service.
  - `instance_count`: The number of instances to deploy for the inference endpoint. A higher count can offer improved performance and handle higher request volumes.
  - `gpu_count`: The number of GPUs assigned to each instance. This is particularly important for computation-intensive models and can significantly affect inference performance.

- `openai_api_key`: The API key for OpenAI, utilized for quality evaluation.
- `sagemaker_session_profile_name`: (Optional) A configured AWS profile name for setting up SageMaker sessions with boto3. Defaults to the default AWS profile on the machine if not specified.
- `project_prefix`: A unique prefix for each deployment within an AWS account, aiding in resource identification.
- `deploy_stage`: The stage of deployment, such as development, staging, or production.
- `deploy_region`: The AWS region where the deployment will occur.
- `ecr_repo`: The name of the ECR repository where the Docker image is pushed.
- `ecr_image_tag`: The tag of the Docker image in ECR.
- `ecr_url`: The URL of the ECR repository.
- `deploy_pipeline`: Boolean to control deployment method (locally or via CDK pipeline). Note that CDK pipeline deployment is experimental.
- `codecommit_repo_name`: The name of the CodeCommit repository, used when deploying via CDK pipeline (experimental).
- `branch`: The branch to use in the CodeCommit repository when deploying via CDK pipeline (experimental).
- `app_container_vcpus`: The number of virtual CPUs allocated for the ECS task running the application.
- `app_container_memory`: The memory allocation (in MB) for the ECS task running the application.
- `app_params`: Application-specific parameters.
  - `INFER_LOCAL`: Should be "false" for non-local development.
  - `DB_LOCAL`: Should be "false" for non-local development.
  - `EMBEDDING_COLLECTION_NAME`: The collection name for embeddings; can be any static string.
  - `OPENAI_API_TYPE`: The type of OpenAI API key being used.
  - `OPENAI_API_VERSION`: The version of the OpenAI API.
  - `OPENAI_API_BASE`: The base URL for the OpenAI API.
  - `OPENAI_DEPLOYMENT_NAME`: The specific deployment name for the OpenAI API key.
  - `USE_BEDROCK`: Boolean to indicate if Bedrock is used for embeddings.
  - `BEDROCK_REGION`: Specifies the AWS region for Bedrock if it's used.


## Deployment Steps in Sandbox AWS Environment

1. **Fetch the Repository**: 


2. **Docker Setup**: 


3. **Set up an aws profile**
    
    `aws configure`

4. **Configuration**: Create a `cdk.json` from the `cdk.template.json`, ensuring to fill in the `openai_api_key` and `huggingface.token_id`.



5. **Deploy** 

    `cdk deploy --all`

By following these steps and understanding each configuration parameter, you can deploy RAGTrack in a sandbox AWS environment efficiently. For any queries or assistance, please reach out to
