import sqlalchemy
from rag_application_framework.db.models.models import Base
from sqlalchemy import text


def inititalize(engine: sqlalchemy.engine.Engine):
    """
    Will only be called once to create the extension and create the tables.
    Many other calls should not do anything.
    Note: A safer option is to create the extension externally from the database.
    Refer, nc-bot/pg_vector/init_db.sql for more information.
    """
    with engine.connect() as cur:
        try:
            cur.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            cur.commit()
        except Exception as e:
            print(e)
    Base.metadata.create_all(engine)
