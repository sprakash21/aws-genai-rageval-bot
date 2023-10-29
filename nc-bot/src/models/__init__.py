import os
import sqlalchemy as db
from src.models.models import Base
from dotenv import load_dotenv

load_dotenv()

def setup_db(self, cur):
    cur.execute("""
                CREATE DATABASE IF NOT EXISTS vectordblab;
                CREATE EXTENSION IF NOT EXISTS vector;
                """
    )

def prepare_connection_str():
    user = os.environ.get('PGVECTOR_USER')
    password = os.environ.get('PGVECTOR_PASSWORD')
    db_name = os.environ.get('PGVECTOR_DATABASE')
    return f'postgresql+psycopg2://{user}:{password}@localhost:5432/{db_name}'

engine = db.create_engine(prepare_connection_str())
# Creation of the tables
Base.metadata.create_all(engine)
