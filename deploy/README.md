# GenAI CDK Setup and Foundation

## Features
This CDK packages acts as a foundation to deploy gen-ai application stack which encompasses:   
1. Deployment of Foundation models from AWS, open source LLM model from HuggingFace into Sagemaker through Deep Learning Containers.  
2. Deployment of the Vector Database required for the underneath application. We currently have used Aurora Postgres with Pgvector only. This could be extended to support for other databases.  
3. Deployment of a QABot application with the quality monitoring capabilities alongside integrated with Amazon Bedrock is also deployed.  

## Deployment Overview

The deployment of QABot is executed through the AWS Cloud Development Kit (CDK), utilizing Python as the programming language. This setup ensures a streamlined deployment process.

### Configuration Parameters

The `cdk.template.json` configuration file outlines the parameters for deployment. You can use the `cdk.template.json` as it is by adding the values for `huggingface.token_id` for open source LLM deployments. 

Below is a detailed description of each parameter:

* `huggingface.token_id`: The token ID for Hugging Face, required for authentication and accessing Hugging Face models.

* `huggingface.llama2.13b`: Configuration settings specific to the Hugging Face 'llama2.13b' model used by the application.
    * `model_id`: The specific model identifier as recognized by Hugging Face. This ID is used to fetch the correct model.
    * `task`: The type of task for which the model is optimized, as defined by Hugging Face. This could be text generation, classification, etc.

* `inference_endpoint`: Settings for the SageMaker inference endpoint, which is the AWS service used to deploy machine learning models for inference.
    * `instance_type`: Specifies the type of instance (e.g., computational power, memory) used for the SageMaker inference endpoint. This determines the capacity and performance of the inference service.
    * `instance_count`: The number of instances to deploy for the inference endpoint. A higher count can offer improved performance and handle higher request volumes.
    * `gpu_count`: The number of GPUs assigned to each instance. This is particularly important for computation-intensive models and can significantly affect inference performance.

* `sagemaker_session_profile_name`: (Optional) A configured AWS profile name for setting up SageMaker sessions with boto3. Defaults to the default AWS profile on the machine if not specified.
* `project_prefix`: A unique prefix for each deployment within an AWS account, aiding in resource identification.
* `deploy_stage`: The stage of deployment, such as development, staging, or production.
* `deploy_region`: The AWS region where the deployment will occur.
* `deploy_account`: The AWS account where the deployment will occur.  
* `ecr_repo`: The name of the ECR repository where the Docker image is pushed.
* `ecr_image_tag`: The tag of the Docker image in ECR.
* `ecr_url`: The URL of the ECR repository.
* `deploy_pipeline`: Boolean to control deployment method (locally or via CDK pipeline). Note that CDK pipeline deployment is experimental.
* `codecommit_repo_name`: The name of the CodeCommit repository, used when deploying via CDK pipeline (experimental).
* `branch`: The branch to use in the CodeCommit repository when deploying via CDK pipeline (experimental).
* `app_container_vcpus`: The number of virtual CPUs allocated for the ECS task running the application.
* `app_container_memory`: The memory allocation (in MB) for the ECS task running the application.
* `app_params`: Application-specific parameters.
    * `DB_LOCAL`: Whether database is locally setup or not (Boolean true or false).
    * `EMBEDDING_COLLECTION_NAME`: your_collection_name.
    * `USE_BEDROCK_EMBEDDINGS`: true/false.
    * `BEDROCK_EMBEDDINGS_REGION`: region.
    * `INFERENCE_ENGINE`: bedrock/sagemaker.
    * `BEDROCK_INFERENCE_REGION`: region, if inference is from bedrock.
    * `BEDROCK_INFERENCE_MODEL_ID`: "meta.llama3-70b-instruct-v1:0".
    * `BEDROCK_EVALUATION_ENGINE`: bedrock.
    * `BEDROCK_EVALUATION_REGION`: region.
    * `BEDROCK_EVALUATION_MODEL_ID`:"anthropic.claude-3-sonnet-20240229-v1:0".
    * `LOGIN_CODE`: initial code for app to get access to.
    * `PGVECTOR_USER`:OPTIONAL: Applies When DB_LOCAL Is True.
    * `PGVECTOR_PASSWORD`:OPTIONAL: Applies When DB_LOCAL Is True.
    * `PGVECTOR_PORT`:5432.
    * `PGVECTOR_HOST`: OPTIONAL: Applies When DB_LOCAL Is True.
    * `PGVECTOR_DATABASE`: OPTIONAL: Applies When DB_LOCAL Is True.

## Steps for deployment
1. Copy the `cdk.template.json` to `cdk.json` and work with the adapting the values in accordance to your needs. For instance, it could model deployments, or adaptation to extend to deploy a new application.  
2. `python3 -m .venv venv` to create the virtual environment and source `.venv/bin/activate` to activate it.  
3. `pip install -r requirements.txt` to install the required cdk related packages. You may require to install cdk from npm as well.  
4. To syntheses the stack run `cdk synth --all` or a stack.  
5. The deployment stack is also setup with cdk-nag to apply and verify the best practises for the deployment of the AWS stack. Note: Some of the not required Error are added into supressions.  
6. To deploy the stack run `cdk deploy --all` or a stack.  
7. If you get "Unable to resolve AWS account to use. It must be either configured when you define your CDK Stack, or through the environment" then export the AWS_PROFILE as export `AWS_PROFILE=<your_profile>`  

# Notes
The Database is enabled with delete protection. This is done as per the best practises in the code. In order to destroy the stack, you will have to perform the following steps from the AWS console:  
1. Go to RDS, Clusters  
2. Select the cluster deployed from the stack and click Modify  
3. At the bottom you should see delete protection, uncheck enable delete protection to destroy the stack with RDS deletion.  