import os
import sqlalchemy as db
from src.models.models import Base
from src.config.app_config import get_db_type
from src.helpers.env_utils import get_secret_info
from dotenv import load_dotenv

load_dotenv()


def setup_db(cur):
    cur.execute(
        """
                CREATE EXTENSION IF NOT EXISTS vector;
                """
    )


def prepare_connection_str(db_local=False):
    if db_local:
        user = os.environ.get("PGVECTOR_USER")
        password = os.environ.get("PGVECTOR_PASSWORD")
        db_name = os.environ.get("PGVECTOR_DATABASE")
        host = os.environ.get("PGVECTOR_HOST")
    else:
        rds_secret_info = get_secret_info(os.environ.get("RDS_SECRET_NAME"))
        host = rds_secret_info["host"]
        db_name = rds_secret_info["dbname"]
        user = rds_secret_info["username"]
        password = rds_secret_info["password"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:5432/{db_name}"


db_local = get_db_type()
engine = db.create_engine(prepare_connection_str(db_local))
# Creation of the tables
Base.metadata.create_all(engine)
