import os
from datasets import load_dataset
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from ragas import evaluate
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-07-01-preview"
os.environ["OPENAI_API_BASE"] = "https://oai-int-azg-we-001.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

if __name__ == "__main__":
    azure_model = AzureChatOpenAI(
    deployment_name="dep-gpt-35-turbo",
    openai_api_base="https://oai-int-azg-we-001.openai.azure.com/",
    openai_api_type="azure",
    openai_api_version="2023-07-01-preview",
    openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
    context_precision.llm = azure_model
    faithfulness.llm = azure_model
    fiqa_eval = load_dataset("explodinggradients/fiqa", "ragas_eval")
    print(fiqa_eval.head())
    fiqa_eval.head()
    #result = evaluate(
    #    fiqa_eval["baseline"].select(range(3)), # selecting only 3
    #    metrics=[
    #        context_precision,
    #        faithfulness
    #    ],
    #)
    #print(result)
