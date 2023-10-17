import os
import psycopg2
from langchain.document_loaders import S3FileLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from dotenv import load_dotenv

load_dotenv()


def get_connection_str():
    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
        host=os.environ.get("PGVECTOR_HOST", "localhost"),
        port=int(os.environ.get("PGVECTOR_PORT", "5432")),
        database=os.environ.get("PGVECTOR_DATABASE", "vectordblab"),
        user=os.environ.get("PGVECTOR_USER", "postgres"),
        password=os.environ.get("PGVECTOR_PASSWORD", "POSTGRES_TEST_123!"),
    )
    return CONNECTION_STRING


def make_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="vectordblab",
        user="postgres",
        password="POSTGRES_TEST_123!",
    )
    cur = conn.cursor()
    return cur

def setup_db(cur):
    cur.execute("""
                CREATE EXTENSION IF NOT EXISTS vector;
                """
    )

def is_existing_collection(cur):
    cur.execute(
        "select exists(select * from information_schema.tables where table_name=%s)",
        ("langchain_pg_collection",),
    )
    status = cur.fetchone()[0]
    return status


def is_file_embedded(cur, fname):
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


def process_data(fname, test_delete=False):
    COLLECTION_NAME = "time_reporting"
    loader = S3FileLoader(bucket=os.environ.get("BUCKET_NAME"), key=fname)
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"], chunk_size=1024, chunk_overlap=50
    )
    documents = loader.load_and_split(text_splitter=text_splitter)
    # TODO: Switch to powerful embeddings like titan, fast-embedding, ada_002 probably
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    curr = make_connection()
    setup_db(curr)
    if is_existing_collection(curr) and test_delete is False:
        s3_fname = f"s3://{os.environ.get('BUCKET_NAME')}/{fname}"
        if is_file_embedded(curr, s3_fname):
            print("Same PDF data is being uploaded and it will not be uploaded")
            return False
        else:
            # Extend vectorstore.
            store = PGVector(
                collection_name=COLLECTION_NAME,
                connection_string=get_connection_str(),
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
            pre_delete_collection=True,
            connection_string=get_connection_str(),
        )
        return True


def retrieve_document_similarity(query):
    COLLECTION_NAME = "time_reporting"
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=get_connection_str(),
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


#dir_name = os.path.dirname(__file__)
#print(dir_name)
#process_data(
#    "pdf_data/ED-Time Reporting & Work Time - Finland-071023-193644.pdf",
#    test_delete=False,
#)
#retrieve_docs()
# cur = make_connection()
# fname = f"s3://{os.environ.get('BUCKET_NAME')}/pdf_data/ED-Time-Reporting-&-Work-Time----Austria-071023-193559.pdf"
# print(is_file_embedded(cur, fname))
