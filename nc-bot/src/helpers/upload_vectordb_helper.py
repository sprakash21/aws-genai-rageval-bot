import os
import json
import psycopg2
from langchain.document_loaders import S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import botocore
import boto3
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings, BedrockEmbeddings
from src.helpers.env_utils import get_secret_info_json
from src.config.app_config import get_embedding_model
from dotenv import load_dotenv


load_dotenv()


class UploadHelper:
    """Uploads the unstructured pdf data into vectordb"""

    def __init__(self, db_local):
        self.boto3_session = boto3
        self.is_local = db_local
        self.use_bedrock = True if os.environ.get("USE_BEDROCK") == "true" else False
        self.rds_secret_info = self.get_rds_info(self.is_local)

    def get_rds_info(self, is_local):
        if not is_local:
            return get_secret_info_json(os.environ.get("RDS_SECRET_NAME"))
        else:
            return {}
    
    def get_connection_str(self):
        """Generates the Connection String required to connect to the Database

        Returns:
            _type_: _description_
        """
        if self.is_local:
            CONNECTION_STRING = PGVector.connection_string_from_db_params(
                driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
                host=os.environ.get("PGVECTOR_HOST"),
                port=int(os.environ.get("PGVECTOR_PORT")),
                database=os.environ.get("PGVECTOR_DATABASE"),
                user=os.environ.get("PGVECTOR_USER"),
                password=os.environ.get("PGVECTOR_PASSWORD"),
            )
        else:
            CONNECTION_STRING = PGVector.connection_string_from_db_params(
                driver="psycopg2",
                host=self.rds_secret_info["host"],
                port=int(self.rds_secret_info["port"]),
                database=self.rds_secret_info["dbname"],
                user=self.rds_secret_info["username"],
                password=self.rds_secret_info["password"],
            )
        return CONNECTION_STRING

    def make_connection(self):
        if self.is_local:
            conn = psycopg2.connect(
                host=os.environ.get("PGVECTOR_HOST"),
                port=os.environ.get("PGVECTOR_PORT"),
                dbname=os.environ.get("PGVECTOR_DATABASE"),
                user=os.environ.get("PGVECTOR_USER"),
                password=os.environ.get("PGVECTOR_PASSWORD"),
            )
        else:
            conn = psycopg2.connect(
                host=self.rds_secret_info["host"],
                port=5432,
                dbname=self.rds_secret_info["dbname"],
                user=self.rds_secret_info["username"],
                password=self.rds_secret_info["password"],
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
        """This function performs the required processing of the data for the given input
        file and puts that into the database.

        Args:
            fname (str): File name store in S3
            test_delete (bool, optional): _description_. Defaults to False.

        Returns:
            bool: Success or Failure of the process
        """
        # Fixed collection and can be extended.
        COLLECTION_NAME = "llm_collection"
        loader = S3FileLoader(bucket=os.environ.get("BUCKET_NAME"), key=fname)
        # Short vs Long chunk
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1024, chunk_overlap=50
        )
        documents = loader.load_and_split(text_splitter=text_splitter)
        # Obtain the embeddings for the documents.
        embedding = get_embedding_model(self.use_bedrock)
        curr = self.make_connection()
        if self.is_existing_collection(curr) and test_delete is False:
            s3_fname = f"s3://{os.environ.get('BUCKET_NAME')}/{fname}"
            if self.is_file_embedded(curr, s3_fname):
                print("Same PDF data is being uploaded and it will not be uploaded")
                curr.close()
                return False
            else:
                # Extend vectorstore.
                store = PGVector(
                    collection_name=COLLECTION_NAME,
                    connection_string=self.get_connection_str(),
                    embedding_function=embedding,
                )
                store.add_documents(documents)
                curr.close()
                return True
        else:
            # Create new set of document store
            vector_store = PGVector.from_documents(
                documents=documents,
                embedding=embedding,
                collection_name=COLLECTION_NAME,
                # pre_delete_collection=True,
                connection_string=self.get_connection_str(),
            )
            curr.close()
            return True

    def retrieve_document_similarity(self, query):
        """Retreive similar documents to the query using similarity search of the embeddings
        Args:
            query (str): The query or question asked by user.
        """
        COLLECTION_NAME = "time_reporting"
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=self.get_connection_str(),
            embedding_function=embedding,
        )
        docs_with_score = vector_store.similarity_search_with_score(query)
        for doc, score in docs_with_score:
            print("-" * 80)
            print("Score: ", score)
            print(doc.page_content)
            print("-" * 80)
