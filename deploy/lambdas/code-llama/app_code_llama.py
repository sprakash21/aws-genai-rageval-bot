import os
import json
import boto3

runtime = boto3.client("runtime.sagemaker")

# Hyperparameters
TOP_K = int(os.environ.get("TOP_K"))
TOP_P = float(os.environ.get("TOP_P"))
DO_SAMPLE = True
TEMPERATURE = float(os.environ.get("TEMPERATURE"))
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS"))
REPETATION_PENALITY = float(os.environ.get("REPETATION_PENALITY"))


def handler(event, context):
    body = json.loads(event["body"])
    prompt = body["prompt"]
    endpoint_name = body["endpoint_name"]

    payload = {
        "text_inputs": prompt,
        "do_sample": True,
        "top_p": TOP_P,
        "temperature": TEMPERATURE,
        "top_k": TOP_K,
        "max_new_tokens": MAX_NEW_TOKENS,
        "repetition_penalty": REPETATION_PENALITY,
        "stop": ["</s>"]
    }

    payload = json.dumps(payload).encode("utf-8")

    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=payload
    )

    model_predictions = json.loads(response["Body"].read())
    generated_text = model_predictions["generated_texts"][0]

    message = {"prompt": prompt, "generated_text": generated_text}

    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {"Content-Type": "application/json"}
    }
