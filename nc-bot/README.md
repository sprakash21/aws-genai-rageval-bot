# RAGTrack: Amazon-Powered Context-Aware QA Bot with Quality Monitoring capabilities

## Introduction
RAGTrack is a context aware QA bot built upon Large Language Model with Quality Monitoring capabilities. The framework includes the component to ingest pdf data into vectordb, Inference with the QA bot through in-context learning, Quality monitoring of the RAG (Retreival Augmented Generation) pipeline against a Judge Model. All of the foundational models are configured to use Amazon Bedrock. Additionally, we offer the capability to also infer from local models or using Amazon Sagemaker endpoint.  

## Project Structure
```
nc-bot
|
|----- pages
|----- pg_vector
|----- scripts
|----- rag_application_framework
        |----- config
        |----- helpers
        |----- models
        |----- handlers
|----- chatbot.py
|----- docker-compose-postgres.yml
|----- docker-compose.yml
|----- Dockerfile
|----- Makefile
|----- requirements.txt
|----- .env.template
```

The project is structure as shown above. The important modules are the rag_application_framework/handlers/ragas_evaluation_and_db_logging_callback_handler.py which includes the callback handling of the RAG pipeline to perform the evaluation and saving the scores in the RagScore Table. The helpers module contain all the necessary helpers for ingestion, inference, and evaluation.  

## Setup the bot locally
We can also setup the local via docker. For this one must do the following activities and we assume that docker is setup already in the machine.  

First setup the .env required for the application. In order to do so, perform the necessary steps:  
1. Copy the nc-bot/environment_templates/.env.local.template as .env and fill in the following values in accordance as shown in the table:  

| KEY                 | VALUE       | Description                                                                                   |
|---------------------|-------------|-----------------------------------------------------------------------------------------------|
| AWS_PROFILE         | AWS_PROFILE | AWS profile                                                                                   |
| AWS_REGION          | AWS_REGION  | AWS region                                                                                    |
| DB_LOCAL         | true,false  | Use Local database or from AWS                                                                |
| PGVECTOR_DATABASE   | dbname      | db name to use test                                                                    |
| PGVECTOR_USER       | postgres    | postgres                                                                                      |
| PGVECTOR_PASSWORD   | pwd         | set a password                                                                                |
| PGVECTOR_PORT       | 5432        | 5432                                                                                          |
| PGVECTOR_HOST       | postgres    | localhost/service_name (if on docker)                                                                                    |
| BUCKET_NAME         | bucket_name | S3 bucket name to be created to store the pdf data and reference                              |
| USE_BEDROCK_EMBEDDINGS         | true,false  | Either to use Amazon titan embeddings or not                                                     |
| BEDROCK_EMBEDDINGS_REGION      | region      | Region of the Amazon bedrock model                                                               |
| EMBEDDING_COLLECTION_NAME      | name of the collection      | name of the collection                                                               |
| INFERENCE_ENGINE      | region      | Region of the Amazon bedrock model                                                               |
| BEDROCK_INFERENCE_REGION      | region      | Region of the Amazon bedrock model for inference                                                               |
| BEDROCK_INFERENCE_MODEL_ID      | model.id  |Model-id of the foundational model on Amazon                                                               |
| BEDROCK_EVALUATION_ENGINE      | bedrock      | Default evaluation supported is bedrock ragas                                                               |
| BEDROCK_EVALUATION_MODEL_ID      | model.id      | Model-id for evaluation using Amazon Bedrock                                               |
| LOGIN_CODE      | test      |  Acts as a login token to the app                                                               |

2. Create the S3 bucket required to store the pdf documents. The bucket_name used will be going into the environment variable BUCKET_NAME.  
```
aws s3api create-bucket --bucket <my-bucket> --profile <my-profile>
```  

3. Create the virtual environment with `python3 -m venv .venv` and install the pip requirements with `pip install -r requirements_aws.txt`  

4. Build and start the postgres local image containing the pgvector extension with the following steps:  
```
# Build the docker image for pg_vector
cd aws-genai-rageval-bot/nc-bot
docker build -t pgvector_local -f pg_vector/Dockerfile .

Run:
# If the app is deployed through docker-compose then run:
docker run \
    --network backend-network --network-alias postgres \
    --name postgresql-container \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=test \
    -d pgvector_local

# If using the database independently then run:
docker run \
    --name postgresql-container \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=test \
    -d pgvector_local
# Refer nc-bot/pg_vector/run_pg_local.txt for more details on the execution.  
```
This should start a local postgres container with pgvector extension installed. Note: One can change the underlying vectordb to another. To verify if everything is alright just login to pgadmin docker container at `http://localhost:5555` and access the database by setting up new connection with the details with username as postgres, password as one you define during the run command as shown above. Note: The host will be service name while using application also deployed through docker otherwise localhost should be fine.    

5. Next, since the database is setup update the .env with the values for the database and setting `DB_LOCAL` to true.  Note: While using chatbot locally on your laptop set the `PGVECTOR_HOST`` as localhost.  
 
6. Run the app locally within your laptop:  
```
# Run the application locally
cd aws-genai-rageval-bot/nc-bot
$streamlit run chatbot.py
```
7. Open `http://localhost:8501`. It should launch our home page.  
![RAGTrack](assets/chatbot.png "RAGTrack")

8. After some queries, you can see that the quality monitoring has started to kick in to monitoring the RAG pipeline.  
![Monitor](assets/quality_monitor.png "Monitoring")

## Setup for Amazon deployment
We have CDK stack to deploy the components into the Amazon infrastructure including the foundational models that could be from Sagemaker or Huggingface. The docker image for the application itself needs to be built and uploaded into ecr for the account. This will then be referenced within the cdk.json. For the creation of the docker image, reference `nc-bot/build_docker_image.txt` and the script at `nc-bot/scripts/build_and_push_docker.sh` for more details.  


## Learnings and Future Work
1. Extending the framework to use multiple judges and take voting on the best scores to choose.   
2. Advancing the methodologies of RAG techniques and testing with other model use cases.  
