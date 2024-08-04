from typing import Dict
import json
from langchain_community.llms.sagemaker_endpoint import LLMContentHandler


class ContentTransformationHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_dict = {"inputs": prompt, "parameters": model_kwargs}
        return json.dumps(input_dict).encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        print("output: ", response_json[0])
        return response_json[0]["generated_text"]
