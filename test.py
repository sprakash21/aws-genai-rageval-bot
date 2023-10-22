import os
import json
import boto3

runtime = boto3.client("runtime.sagemaker")

# Hyperparameter


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

def handler():
    messages = [
    {
        "role": "system",
        "content": "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."
    }
    ]
    messages.append({"role": "user", "content": """Context: assignments). This includes dailies, reading/studying various sources to find solutions for customer delivery related issue/task or testing

the solution, peer meeting when going through customer delivery related items or any other meetings related to customer delivery which

we might have, even customer is not present.

If needed, we can adjust in retrospect for example if customers would for whatever reason push back on any of the hours reported on

them.

require us to send this detailed information as an attachment to the invoices). NOTE: Notes will be visible for the customer and those are

required for customer billable work. Therefore, please pay attention to language and clear commenting.

If you are not sure to which assignment to report your time, for any reason, please consult your Team Leader or your Delivery Leader.

Report your hours with 30 min precision (NOTE! This applies to others than PES people)

b. Person handles local taxation, receiving same salary as in original contract

c. No relocation costs are covered

d. Need to be agreed with people leader

For other travel needs, following list of items impacts the decision, hence case by case evaluation and approval from POPS

(+stakeholders) is needed but no general consent exists

Personnel related issues

Insurance (if employer pays travel=work travel), if employer is not paying travel, it's not a work trip

Personal taxations

Data for our customer billing and accounting (enables us to send invoices and manage project budgets)

Data for your work time tracking (mandated by law, in order to control overwork, follow work life balance, etc.)

Important for correct salary payments (e.g. emergency work, overtime)

Input for our business development, in terms of estimating future projects and planning our recruitments

General Rules"""})
    prompt = "How do I report time?"
    messages.append({"role": "user", "content": prompt})
    instruction = build_llama2_prompt(messages)
    payload = {
        "inputs": instruction,
        "parameters": {
            "do_sample": True,
            "top_p": 0.6,
            "temperature": 0.5,
            "top_k": 50,
            "max_new_tokens": 512,
            "repetition_penalty": 1.05,
            "stop": ["</s>"]
        },
    }

    payload = json.dumps(payload).encode("utf-8")

    response = runtime.invoke_endpoint(
        EndpointName="endpoint-meta-llama--Llama-2-13b-chat-hf", ContentType="application/json", Body=payload
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

print(handler())