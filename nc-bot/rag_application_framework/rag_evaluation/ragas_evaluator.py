import logging
import os
from datasets import Dataset
from rag_application_framework.config.app_config import OpenAIConfig, EvaluationConfig
from rag_application_framework.logging.logging import Logging
from langchain_community.chat_models.bedrock import BedrockChat
from langchain.schema.embeddings import Embeddings
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
        #openai_config: OpenAIConfig,
        evaluation_config: EvaluationConfig,
        embeddings: Embeddings,
    ):
        #os.environ.setdefault("OPENAI_API_KEY", "")
        #self.opeai_config = openai_config
        self.evaluation_confg = evaluation_config
        self.embeddings = embeddings
        # Bedrock Judge
        self.judge_model = BedrockChat(
            client=self.evaluation_confg.bedrock_client,
            model_id=str(self.evaluation_confg.bedrock_model_id),
            model_kwargs={"temperature": 0.2, "top_p": 1, "max_tokens": 4000, "top_k": 250},
        )

    def create_dataset(self, run_data: dict):
        """

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

    def evaluate(self, run_data: dict):
        """Performs evaluation using Anthropic Claude-v3-Sonnet as judge for the answer generated from
        LLM family like llama2, llama3. Note: The judge can be any judge. We here use Anthropic Claude Sonnet.

        Args:
            run_data (dict): The dataset to be evaluated

        Returns:
            dict: Scores
        """
        from ragas.metrics import (
            answer_relevancy,
            faithfulness,
            context_utilization,
        )
        from ragas.metrics.critique import correctness
        from ragas import evaluate

        data = self.create_dataset(run_data)

        result = evaluate(
            dataset=data,
            metrics=[
                context_utilization,
                faithfulness,
                answer_relevancy,
                correctness,
            ],
            llm=self.judge_model,
            embeddings=self.embeddings
        )
        return result
