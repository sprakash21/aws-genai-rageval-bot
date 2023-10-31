import os
import json
from src.helpers.inference_helper import Llama2InferenceHelper


def lambda_handler(event, context):
    # Handle the inference of the QA bot
    collection_name = os.environ.get("COLLECTION_NAME", "time_reporting")
    endpoint = os.environ.get("LLAMA2_ENDPOINT", "time_reporting")
    query = event["query"]
    llama2_inf = Llama2InferenceHelper(
        collection_name=collection_name, endpoint=endpoint
    )
    response = llama2_inf.inference(query=query)
    return {
        "status": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"},
    }
