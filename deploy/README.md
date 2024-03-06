
# GenAI CDK Setup and Foundation

## Features
This CDK packages acts as a foundation to deploy gen-ai application stack which encompasses:   
1. Deployment of Foundation models from AWS, open source LLM model from HuggingFace into Sagemaker through Deep Learning Containers.  
2. Deployment of the Vector Database required for the underneath application. We currently have used Aurora Postgres with Pgvector only. This could be extended to support for other databases.  
3. Deployment of a QABot application with the quality monitoring capabilities alongside integrated with Amazon Bedrock is also deployed.  

## Steps for deployment
1. Copy the cdk.template.json to cdk.json and work with the adapting the values in accordance to your needs. For instance, it could model deployments, or adaptation to extend to deploy a new application.  
2. python3 -m .venv venv to create the virtual environment and source .venv/bin/activate to activate it.  
3. pip install -r requirements.txt to install the required cdk related packages. You may require to install cdk from npm as well.  
4. To syntheses the stack run cdk synth --all or a stack.  
5. To deploy the stack run cdk deploy --all or a stack.  
