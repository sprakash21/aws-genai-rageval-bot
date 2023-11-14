import logging
import os
from datasets import Dataset
from rag_application_framework.config.app_config import OpenAIConfig
from rag_application_framework.logging.logging import Logging

from langchain.schema.embeddings import Embeddings
from langchain.chat_models.azure_openai import AzureChatOpenAI


logger = Logging.get_logger(__name__)


class RagasEvaluator:
    """This class performs the evaluation using the ragas framework for:
    a) faithfulness
    b) context_precision
    c) answer_relevancy
    d) harmfulness
    """

    def __init__(
        self,
        openai_config: OpenAIConfig,
        embeddings: Embeddings,
    ):
        self.opeai_config = openai_config
        self.embeddings = embeddings

        os.environ.setdefault("OPENAI_API_KEY", self.opeai_config.api_key)

        self.judge_model = AzureChatOpenAI(
            deployment_name=self.opeai_config.deployment_name,
            openai_api_base=self.opeai_config.api_base,
            openai_api_type=self.opeai_config.api_type,
            openai_api_version=self.opeai_config.api_version,
            openai_api_key=self.opeai_config.api_key,
        )

    def create_dataset(self, run_data):
        """_summary_

        Args:
            run_data (dict): Dictionary information of the run data consisting of question, contexts and answer

        Returns:
            Dataset: dataset in ragas format
        """

        data_dict = {
            "question": [run_data["question"]],
            "contexts": [run_data["contexts"]],
            "answer": [run_data["output_text"]],
        }
        return Dataset.from_dict(data_dict)

    def evaluate(self, run_data):
        """Performs evaluation using chatgpt as judge for the answer generated from
        LLM like llama2. Note: The judge can be any judge. We here use ChatGPT.

        Args:
            run_data (Dataset): The dataset to be evaluated

        Returns:
            dict: Scores
        """
        from ragas.metrics import (
            answer_relevancy,
            faithfulness,
            context_precision,
        )
        from ragas.metrics.critique import harmfulness
        from ragas import evaluate

        data = self.create_dataset(run_data)

        context_precision.llm = self.judge_model
        faithfulness.llm = self.judge_model

        answer_relevancy.embeddings = self.embeddings
        harmfulness.embeddings = self.embeddings

        answer_relevancy.llm = self.judge_model
        harmfulness.llm = self.judge_model

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
