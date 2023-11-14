import sqlalchemy
from rag_application_framework.db.models.models import Base
from sqlalchemy import text


def inititalize(engine: sqlalchemy.engine.Engine):
    if not globals().get("_DB_INITIALIZED", False):
        with engine.connect() as cur:
            try:
                cur.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                cur.commit()
                print("Vector extension created")
            except Exception as e:
                print(e)
        Base.metadata.create_all(engine)
    globals()["_DB_INITIALIZED"] = True
