import os
from datasets import Dataset
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from ragas.metrics.critique import harmfulness
from ragas import evaluate
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

class EvalHelper:
    def __init__(self) -> None:
        self.openai_type = "azure"
        self.openai_api_version = "2023-07-01-preview"
        self.openai_base = "https://oai-int-azg-we-001.openai.azure.com/"
        self.openai_deployment_name = "dep-gpt-35-turbo"
        self.openai_key = os.environ.get("OPENAI_API_KEY")
    
    def create_dataset(self, run_data):
        data_dict = {
            "question": [run_data["question"]],
            "contexts": [run_data["contexts"]],
            "answer": [run_data["output_text"]]
        }
        print(data_dict)
        return Dataset.from_dict(data_dict)
    
    def evaluation(self, run_data):
        data = self.create_dataset(run_data)
        azure_model = AzureChatOpenAI(
            deployment_name=self.openai_deployment_name,
            openai_api_base=self.openai_base,
            openai_api_type=self.openai_type,
            openai_api_version=self.openai_api_version,
            openai_api_key=self.openai_key
            )
        context_precision.llm = azure_model
        faithfulness.llm = azure_model
        answer_relevancy.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        answer_relevancy.llm = azure_model
        harmfulness.llm = azure_model
        harmfulness.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        result = evaluate(dataset=data, metrics=[context_precision,faithfulness, answer_relevancy, harmfulness])
        return result
