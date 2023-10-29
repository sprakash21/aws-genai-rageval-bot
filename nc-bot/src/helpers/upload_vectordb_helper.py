import os
import json
import psycopg2
from langchain.document_loaders import S3FileLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)
import botocore
import boto3
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv


load_dotenv()

class UploadHelper:
    def __init__(self, local=False):
        if local:
            self.boto3_session = boto3.Session(profile_name=os.environ.get("AWS_PROFILE"))
            self.is_local = True
        else:
            self.boto3_session = boto3
            self.is_local = False
    
    def get_db_secret_info(self):
        try:
            client = self.boto3_session.client("secretsmanager")
            response = client.get_secret_value(
                SecretId='RDS_postgres'
            )
            return json.loads(response['SecretString'])
        except botocore.exceptions.ClientError as exc:
            print('There has been an error while obtaining secret information', exc)

    def get_connection_str(self):
        if self.is_local:
            CONNECTION_STRING = PGVector.connection_string_from_db_params(
                driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
                host=os.environ.get("PGVECTOR_HOST"),
                port=int(os.environ.get("PGVECTOR_PORT")),
                database=os.environ.get("PGVECTOR_DATABASE"),
                user=os.environ.get("PGVECTOR_USER"),
                password=os.environ.get("PGVECTOR_PASSWORD")
            )
        else:
            secret_info = self.get_db_secret_info()
            CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=secret_info["host"],
            port=int(secret_info["port"]),
            database=secret_info["dbname"],
            user=secret_info["username"],
            password=secret_info["password"]
        )
        return CONNECTION_STRING


    def make_connection(self):
        if self.is_local:
            conn = psycopg2.connect(
                host=os.environ.get("PGVECTOR_HOST"),
                port=os.environ.get("PGVECTOR_PORT"),
                dbname=os.environ.get("PGVECTOR_DATABASE"),
                user=os.environ.get("PGVECTOR_USER"),
                password=os.environ.get("PGVECTOR_PASSWORD")
        )
        else:
            secret_info = self.get_db_secret_info()
            print(secret_info)
            conn = psycopg2.connect(
                host=secret_info["host"],
                port=5432,
                dbname=secret_info["dbname"],
                user=secret_info["username"],
                password=secret_info["password"],
            )
        cur = conn.cursor()
        return cur


    def is_existing_collection(self, cur):
        cur.execute(
            "select exists(select * from information_schema.tables where table_name=%s)",
            ("langchain_pg_collection",),
        )
        status = cur.fetchone()[0]
        return status


    def is_file_embedded(self, cur, fname):
        query = """
        select count(*) as counts
        from langchain_pg_embedding as embed
        where embed.cmetadata ->> 'source'=%s
        """
        cur.execute(query, (fname,))
        counts = cur.fetchone()[0]
        if counts > 0:
            return True
        return False

    def process_data(self, fname, test_delete=False):
        COLLECTION_NAME = "time_reporting"
        loader = S3FileLoader(bucket=os.environ.get("BUCKET_NAME"), key=fname)
        # Short vs Long chunk
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1024, chunk_overlap=50
        )
        documents = loader.load_and_split(text_splitter=text_splitter)

        # TODO: Switch to powerful embeddings like titan, fast-embedding, ada_002 probably
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        curr = self.make_connection()
        if self.is_existing_collection(curr) and test_delete is False:
            s3_fname = f"s3://{os.environ.get('BUCKET_NAME')}/{fname}"
            if self.is_file_embedded(curr, s3_fname):
                print("Same PDF data is being uploaded and it will not be uploaded")
                return False
            else:
                # Extend vectorstore.
                store = PGVector(
                    collection_name=COLLECTION_NAME,
                    connection_string=self.get_connection_str(),
                    embedding_function=embedding,
                )
                store.add_documents(documents)

                return True
        else:
            # Create new set of document store
            vector_store = PGVector.from_documents(
                documents=documents,
                embedding=embedding,
                collection_name=COLLECTION_NAME,
                #pre_delete_collection=True,
                connection_string=self.get_connection_str(),
            )
            return True


    def retrieve_document_similarity(self, query):
        COLLECTION_NAME = "time_reporting"
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=self.get_connection_str(),
            embedding_function=embedding,
        )
        docs_with_score = vector_store.similarity_search_with_score(
            query
        )
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80)
