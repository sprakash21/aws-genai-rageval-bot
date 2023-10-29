import asyncio
from datetime import datetime
from time import time
from collections import defaultdict
from typing import List, Dict, Any, DefaultDict, Dict
from langchain.callbacks.base import BaseCallbackHandler
from langchain.llms.base import LLMResult
from sqlalchemy.orm import Session
from src.models import engine
from src.models.models import RagScore
from src.helpers.evaluation_helper import EvalHelper

class DBCallbackHandler(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""
    def __init__(self) -> None:
        self.run_data_llm: DefaultDict[str, Any] = defaultdict(dict)
        self.run_data_chain: DefaultDict[str, Any] = defaultdict(dict)
        super().__init__()
    
    def process_llama2_prompt(self, prompt: str) -> Any:
        question_raw = prompt.split("Context:")[0].split("Question:")[1].strip()
        context_raw = prompt.split("Context:")[1].replace("Answer: [/INST]", "").strip()
        return question_raw, context_raw

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        run_id = kwargs["run_id"]
        print("Run id LLM Start", run_id)
        self.run_data_llm[run_id]["prompts"] = prompts
        self.run_data_llm[run_id]["start_time"] = time()
        print("on_llm_start Prompt --", prompts)
        print("on_llm_start Seralized --", serialized)

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
                run_data_llm["model_type"] = generation.generation_info["model"]
                run_data_llm["qa_status"] = generation.generation_info["done"]
                self.run_data_llm[run_id] = run_data_llm

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        run_id = kwargs["run_id"]

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
        if kwargs["run_id"] in self.run_data_chain.keys():
            self.run_data_chain[kwargs["run_id"]]["output_text"] = outputs["output_text"]
        
            combined_dict = dict()
            for value in self.run_data_llm.values():
                combined_dict.update(value)
            for value in self.run_data_chain.values():
                combined_dict.update(value)
            evaluation_helper = EvalHelper()
            result = evaluation_helper.evaluation(run_data=combined_dict)
            print(result)
            with Session(engine) as session:
                rag_score = RagScore(
                    chain_info = {
                        "question": combined_dict["question"],
                        "contexts": combined_dict["contexts"],
                        "answer": combined_dict["output_text"]},
                    model_type=combined_dict["model_type"],
                    qa_status=combined_dict["qa_status"],
                    total_duration=combined_dict["total_duration"],
                    faithfulness=result["faithfulness"],
                    context_precision=result["context_precision"],
                    answer_relevancy=result["answer_relevancy"],
                    harmfulness=result["harmfulness"],
                    time_stamp=datetime.utcnow(),
                )
                session.add(rag_score)
                session.commit()
                session.close()

        


    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Do nothing."""
        pass
