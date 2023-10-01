# Generative AI: Investigating the service offerings.
What is Generative AI?  
In the previous years, traditional machine learning was always related with performing a task trained on dataset to provide inference. If there involved multiple tasks then there required approaches of multiple models to handle such scenarios and not generative in nature. The generative AI thus helps in generating new content or help with processing the data for understand. This technique is powered by Large Language Models (LLM) which are pretrained on Large amount of data also known as Foundational Models.

With small amount of custom data, a foundation model could be fine tuned and tailored to the required needs for the use cases.  

# AWS Offerring
### AWS Sagemaker:  
Foundation models can already be built and consumed through the lambda as api for inference. For example, a model to perform text summarization can be deployed through Sagemaker Jumpstart (from the available list) and be consumed for inference. With the easy integration with Hugging Face, many open source models can be utilized and fine tuned as well. 

Points:  
1. The agents and other related things will not come built-in will have to be built separately.  
2. Cost: Cost of the instances where the model might be deployed might highly differ. For most use cases it really depends on the number of parametes and sweet spot is from 7B - 20B and beyond it will be a most likely a very high use case scenario. Some of them could fit into a lower GPU models thus not increasing costs.   
3. Performance: The performance of the inference speed will solely depend on the instance type under the hood and the design of the system as a whole plus the way the model is tuned.  
4. Security: The security pillar of AWS is integrated already and is covered nothing new here is required.  

### AWS Bedrock:  
AWS Bedrock is a fully managed (serverless) service that allows to quickly spin up a Foundation Models (FM) from amazon or other third party. This allows quickly using many FM which could be right fit for the use case under consideration.  

Features:  
1. Bedrock has agents which allows to create genAI application that use latest informations from the knowledge base to deliver up-to-date results.  
2. Accessing FM easily via a single API experience.  
3. Ability to fine-tune on custom data and build custom models. Models are securely stored in S3 and encrypted with KMS without requiring to maintain the infrastructure.   
4. Connecting the FM to companies knowledge through Retreival Augmented Generation (RAG). The sources for the data to be ingested can be in S3, followed by a FM which can convert the text --> vector embeddings (char, word, sentences level) --> Be stored into Vector database (AWS offers: Elastic-Search, Redis, etc...) from which for the query similar context can be obtained and be provided for making right decision and avoiding hallucinations of the model.  

Points:  
1. Costs: Although there is no very detailed information yet. It is costly when running very large models and one will need to be aware of it.  

AWS Bedrock although states the support as a fully managed service for the models. Not all model fine-tunining is fully handled and the pricing for fine tuning would become same as using with Sagemaker and could also get costlier.

2. Security: Integrates very well with AWS ecosystem where the require security measures can be implemented.  
3. Tasks and availability:  
Update: AWS Bedrock is now generally available and no more in preview. Very soon llama2 will be added.  


General Notes:  
AWS is putting money with Anthropic to build safe LLM models and competing against open-ai.  
Huggingface partnerships with AWS to make AI accessible via AWS Sagemaker.  