import os
import json
import boto3

runtime = boto3.client("runtime.sagemaker")

# Hyperparameters
MAX_LENGTH = 1024
NUM_RETURN_SEQUENCES = 1
TOP_K = 0
TOP_P = 0.9
TEMPERATURE = 0.8
REPETATION_PENALITY = 1.03
DO_SAMPLE = True
SM_ENDPOINT_NAME = os.environ.get("SM_ENDPOINT_NAME")


def handler(event, context):
    body = json.loads(event["body"])
    prompt = body["prompt"]
    payload = {
        "text_inputs": prompt,
        "temparuture": TEMPERATURE,
        "do_sample": True,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "max_length": MAX_LENGTH,
        "num_return_sequences": NUM_RETURN_SEQUENCES,
        "repetition_penalty": REPETATION_PENALITY,
        "stop": ["\nUser:", "<|endoftext|>", "</s>"],
    }
    payload = json.dumps(payload).encode("utf-8")

    response = runtime.invoke_endpoint(
        EndpointName=SM_ENDPOINT_NAME, ContentType="application/json", Body=payload
    )

    model_predictions = json.loads(response["Body"].read())
    generated_text = model_predictions["generated_texts"][0]

    message = {"prompt": prompt, "generated_text": generated_text}

    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {"Content-Type": "application/json"},
    }
