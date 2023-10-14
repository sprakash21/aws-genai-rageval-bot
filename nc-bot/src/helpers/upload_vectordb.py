import os
from langchain.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
def process_data(fname):
    loader = S3FileLoader(bucket=os.environ.get("BUCKET_NAME"), key=fname)
    documents = loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    pages = text_splitter.split_documents(documents)
    for page in pages:
        print(page)
    

dir_name = os.path.dirname(__file__)
print(dir_name)
process_data("pdf_data/ED-Time-Reporting-&-Work-Time----Austria-071023-193559.pdf")
