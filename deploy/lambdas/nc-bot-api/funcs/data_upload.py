import json
from src.helpers.uploading_helper import UploadHelper

# AWS magic
import nltk


def pre_setup():
    nltk_data_path = "/tmp/nltk_data"
    nltk.download("stopwords", download_dir=nltk_data_path)
    nltk.download("punkt", download_dir=nltk_data_path)
    nltk.download("wordnet", download_dir=nltk_data_path)


def lambda_handler(event, context):
    pre_setup()
    # Handling of the data upload of pdf into vectorstore
    upload_helper = UploadHelper(local=False)
    file_path = event["file_path"]
    status = upload_helper.process_data(file_path)
    message = {"upload_status": status, "message": "File upload is successful"}
    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {"Content-Type": "application/json"},
    }
