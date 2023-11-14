from collections import defaultdict
from datetime import datetime
from time import time
from typing import Any, DefaultDict, Dict, List

import sqlalchemy
from langchain.callbacks.base import BaseCallbackHandler
from rag_application_framework.config.app_config import EmbeddingConfig, OpenAIConfig
from rag_application_framework.db.models.models import RagScore
from rag_application_framework.logging.logging import Logging
from rag_application_framework.rag_evaluation.ragas_evaluator import RagasEvaluator
from sqlalchemy.orm import Session
from langchain.schema import LLMResult

logger = Logging.get_logger(__name__)


class RagasEvaluationAndDbLoggingCallbackHandler(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""

    def __init__(
        self,
        openai_config: OpenAIConfig,
        embeddings_config: EmbeddingConfig,
        engine: sqlalchemy.engine.Engine,
    ) -> None:
        self.run_data_llm: DefaultDict[str, Any] = defaultdict(dict)
        self.run_data_chain: DefaultDict[str, Any] = defaultdict(dict)
        super().__init__()
        self.openai_config = openai_config
        self.embeddings_config = embeddings_config
        self.engine = engine

    def process_llama2_prompt(self, prompt: str) -> Any:
        question_raw = prompt.split("Context:")[0].split("Question:")[1].strip()
        context_raw = prompt.split("Context:")[1].replace("Answer: [/INST]", "").strip()
        return question_raw, context_raw

    def evaluate(self, response_data: dict) -> dict:
        evaluation_helper = RagasEvaluator(
            openai_config=self.openai_config,
            embeddings=self.embeddings_config.embeddings,
        )
        logger.info("Evaluation Started.")
        result = evaluation_helper.evaluate(run_data=response_data)
        logger.info("Evaluation Complete. Result of the evaluation: \n %s", result)
        return result

    def write_score(self, response_data: dict):
        result = self.evaluate(response_data)
        if len(result) == 0:
            logger.error("The evaluation of the result was not successful")
        with Session(self.engine) as session:
            rag_score = RagScore(
                chain_info={
                    "question": response_data["question"],
                    "contexts": response_data["contexts"],
                    "answer": response_data["output_text"],
                },
                model_type=response_data["model_type"],
                qa_status=response_data["qa_status"],
                total_duration=response_data["total_duration"],
                faithfulness=result["faithfulness"],
                context_precision=result["context_precision"],
                answer_relevancy=result["answer_relevancy"],
                harmfulness=result["harmfulness"],
                time_stamp=datetime.utcnow(),
            )
            session.add(rag_score)
            session.commit()
            logger.info("Score written to the database: %s", rag_score)
            session.close()

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        run_id = kwargs["run_id"]
        logger.info("Run id LLM Start: %s", run_id)
        self.run_data_llm[run_id] = {}
        self.run_data_llm[run_id]["prompts"] = prompts
        self.run_data_llm[run_id]["start_time"] = time()
        logger.info("on_llm_start Prompt -- %s", str(prompts))
        logger.info("on_llm_start Seralized -- %s", str(serialized))

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        run_id = kwargs["run_id"]
        try:
            run_data_llm = self.run_data_llm[run_id]
            print("Run id LLM", run_id)
        except KeyError as e:
            raise KeyError(
                "This function has been called with a run_id"
                " that was never registered in on_llm_start()."
                " Restart and try running the LLM again"
            ) from e
        # mark the duration time between on_llm_start() and on_llm_end()
        time_from_start_to_end = time() - run_data_llm["start_time"]
        print("LLM end response", response)
        for i, generations in enumerate(response.generations):
            for generation in generations:
                run_data_llm["total_duration"] = time_from_start_to_end
                if hasattr(generations, "generation_info"):
                    run_data_llm["model_type"] = generation.generation_info["model"]
                    run_data_llm["qa_status"] = generation.generation_info["done"]
                else:
                    run_data_llm["model_type"] = "sagemaker_endpoint"
                    run_data_llm["qa_status"] = (
                        True
                        if (hasattr(generation, "text")) and (len(generation.text) > 0)
                        else False
                    )
                self.run_data_llm[run_id] = run_data_llm

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        run_id = kwargs["run_id"]
        logger.info("Chain Started: %s", run_id)
        if isinstance(inputs, dict) and "input_documents" in inputs:
            contexts = []
            for document in inputs["input_documents"]:
                if isinstance(document, dict):
                    contexts.append(document["page_content"])
                else:
                    contexts.append(document.page_content)
            self.run_data_chain[run_id]["contexts"] = contexts
            self.run_data_chain[run_id]["question"] = inputs["question"]

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        logger.info("Chain Ended: %s", kwargs["run_id"])
        if kwargs["run_id"] in self.run_data_chain.keys():
            self.run_data_chain[kwargs["run_id"]]["output_text"] = outputs[
                "output_text"
            ]
            combined_dict = dict()
            for value in self.run_data_llm.values():
                combined_dict.update(value)
            for value in self.run_data_chain.values():
                combined_dict.update(value)

            self.write_score(combined_dict)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Do nothing."""
        pass
