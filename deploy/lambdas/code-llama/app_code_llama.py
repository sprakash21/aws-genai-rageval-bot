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
SM_ENDPOINT_NAME = os.environ.get("SM_ENDPOINT_NAME")


def build_llama2_prompt(messages):
    start_prompt = "<s>[INST] "
    end_prompt = " [/INST]"
    conversation = []
    for index, message in enumerate(messages):
        if message["role"] == "system" and index == 0:
            conversation.append(f"<<SYS>>\n{message['content']}\n<</SYS>>\n\n")
        elif message["role"] == "user":
            conversation.append(message["content"].strip())
        else:
            conversation.append(f" [/INST] {message['content'].strip()}</s><s>[INST] ")

    return start_prompt + "".join(conversation) + end_prompt

def handler(event, context):
    messages = [
    {
        "role": "system",
        "content": "You're an intelligent, concise coding assistant. Wrap code in ``` for readability. Don't repeat yourself. Use best practice and good coding standards."
    }
    ]
    body = json.loads(event["body"])
    prompt = body["prompt"]
    messages.append({"role": "user", "content": prompt})
    instruction = build_llama2_prompt(messages)
    payload = {
        "inputs": instruction,
        "parameters": {
            "do_sample": True,
            "top_p": TOP_P,
            "temperature": TEMPERATURE,
            "top_k": TOP_K,
            "max_new_tokens": MAX_NEW_TOKENS,
            "repetition_penalty": REPETATION_PENALITY,
            "stop": ["</s>"]
        },
    }

    payload = json.dumps(payload).encode("utf-8")

    response = runtime.invoke_endpoint(
        EndpointName=SM_ENDPOINT_NAME, ContentType="application/json", Body=payload
    )

    model_predictions = json.loads(response["Body"].read())
    print(model_predictions)
    generated_text = model_predictions[0]["generated_text"][len(instruction):]

    message = {"prompt": prompt, "generated_text": generated_text}

    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {"Content-Type": "application/json"},
    }
