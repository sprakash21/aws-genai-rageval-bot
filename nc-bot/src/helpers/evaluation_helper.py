import os
from src.helpers.env_utils import get_secret_info
from datasets import Dataset
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_precision,
)
import asyncio
from ragas.metrics.critique import harmfulness
from ragas import evaluate
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()


class EvalHelper:
    """This class performs the evaluation using the ragas framework for:
    a) faithfulness
    b) context_precision
    c) answer_relevancy
    d) harmfulness
    """

    def __init__(self) -> None:
        self.openai_type = "azure"
        self.openai_api_version = "2023-07-01-preview"
        self.openai_base = "https://oai-int-azg-we-001.openai.azure.com/"
        self.openai_deployment_name = "dep-gpt-35-turbo"
        self.openai_key = get_secret_info(os.environ.get("OPENAI_API_KEY_NAME"))[
            "token"
        ]

    async def create_dataset(self, run_data):
        """_summary_

        Args:
            run_data (dict): Dictionary information of the run data consisting of question, contexts and answer

        Returns:
            Dataset: dataset in ragas format
        """
        print("Came here -- CreateDataset")
        data_dict = {
            "question": [run_data["question"]],
            "contexts": [run_data["contexts"]],
            "answer": [run_data["output_text"]],
        }
        return Dataset.from_dict(data_dict)

    async def evaluation(self, run_data):
        """Performs evaluation using chatgpt as judge for the answer generated from 
        LLM like llama2. Note: The judge can be any judge. We here use ChatGPT.

        Args:
            run_data (Dataset): The dataset to be evaluated

        Returns:
            dict: Scores
        """
        try:
            print("Came here -- Evaluation")
            if self.openai_key == "":
                raise AssertionError(
                    "The key is empty. Check the value at the secrets manager"
                )
            data = await self.create_dataset(run_data)
            azure_model = AzureChatOpenAI(
                deployment_name=self.openai_deployment_name,
                openai_api_base=self.openai_base,
                openai_api_type=self.openai_type,
                openai_api_version=self.openai_api_version,
                openai_api_key=self.openai_key,
            )
            context_precision.llm = azure_model
            faithfulness.llm = azure_model
            answer_relevancy.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            answer_relevancy.llm = azure_model
            harmfulness.llm = azure_model
            harmfulness.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            print("Came here -- Evaluation Starting...")
            result = evaluate(
                dataset=data,
                metrics=[
                    context_precision,
                    faithfulness,
                    answer_relevancy,
                    harmfulness,
                ],
            )
            return result
        except Exception as e:
            print("There has been an error with the request", e)
            return {}
