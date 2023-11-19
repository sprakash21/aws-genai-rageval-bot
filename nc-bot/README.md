# RAGTrack: AWS-Powered Context-Aware QA Bot with Quality Monitoring capabilities

## Introduction
RAGTrack is a context aware QA bot built upon Llama2 with Quality Monitoring capabilties. The framework includes the component to ingest pdf data into vectordb, Inference with the QA bot through in-context learning, Quality monitoring of the RAG (Retreival Augmented Generation) pipeline.

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

## Chatbot Home Page
<TODO: Add the home page>

## Setup the bot locally
We can also setup the local via docker. For this one must do the following activities and we assume that docker is setup already in the machine.  

First setup the .env required for the application. In order to do so, perform the necessary steps:  
1. Copy the .env.template as .env and fill in the following values in accordance as shown in the table:  

| KEY                 | VALUE       | Description                                                                                   |
|---------------------|-------------|-----------------------------------------------------------------------------------------------|
| AWS_PROFILE         | AWS_PROFILE | AWS profile                                                                                   |
| AWS_REGION          | AWS_REGION  | AWS region                                                                                    |
| IS_DB_LOCAL         | true,false  | Use Local database or from AWS                                                                |
| PGVECTOR_DATABASE   | dbname      | db name to use vectordblab                                                                    |
| PGVECTOR_USER       | postgres    | postgres                                                                                      |
| PGVECTOR_PASSWORD   | pwd         | set a password                                                                                |
| PGVECTOR_PORT       | 5432        | 5432                                                                                          |
| PGVECTOR_HOST       | postgres    | localhost?                                                                                    |
| SAGEMAKER_ENDPOINT_SSM_PARAM_NAME    | ssm_param   | Optional: SSM parameter store name for Sagemaker endpoint created from CDK if using Sagemaker |
| RDS_POSTRGRES_CREDENTIALS_SECRET_NAME     | SecretName  | Optional: RDS Secret name for created from CDK if using RDS and IS_LOCAL_DB is false          |
| OPENAI_API_KEY_SECRET_NAME | token       | Required to use evaluation of the RAG pipeline using ragas                                    |
| BUCKET_NAME         | bucket_name | S3 bucket name to be created to store the pdf data and reference                              |
| USE_BEDROCK_EMBEDDINGS         | true,false  | Either to use aws titan embeddings or not                                                     |
| BEDROCK_EMBEDDINGS_REGION      | region      | Region of the aws bedrock model                                                               |

2. Create the virtual environment with `python3 -m venv .venv` and install the pip requirements with `pip install -r requirements.txt`  

3. Start the postgres local image containing the pgvector extension with the following steps:  
```
# Password in the docker-compose-postgres.yml
$make build-pgvector-local
$make run-pgvector-local
```
This should start a local postgres container with pgvector extension installed. Note: One can change the underlying vectordb to another. The benchmarking of various vectordbs are in our roadmap. To verify if everything is alright just login to pgadmin docker container at `http://localhost:5555` and access the database by setting up new connection with the details with username as postgres, password as one you define in the docker-compose-postgres.yml for both postgres and pgadmin. Note: The host will be service name while using docker and will be called as postgres while using through pgadmin.  

4. Next, since the database is setup update the .env with the values for the database and setting `IS_LOCAL_DB` to true.  Note: While using chatbot locally on your laptop set the `PGVECTOR_HOST`` as localhost.  

5. Download and install ollama (https://ollama.ai/)[Ollama] and pull llama2 for 7b or 13b. Note: You can also play around with some other model. You will need a laptop that is atleast quite high in configurations with multicore and about 16 to 32 GB of RAM.  
```
ollama pull llama2:7b|13b
ollama run llama2:7b|13b
/bye
```
5. Run the app locally within your laptop:  
```
# Change the function at chatbot.py from inference(prompt) to inference_local(prompt) to run locally using ollama
$streamlit run chatbot.py
```
6. Open `http://localhost:8501`. It should launch our home page.  
![RAGTrack](assets/chatbot.png "RAGTrack")

7. After some queries, you can see that the quality monitoring has started to kick in to monitoring the RAG pipeline.  
![Monitor](assets/quality_monitor.png "Monitoring")
