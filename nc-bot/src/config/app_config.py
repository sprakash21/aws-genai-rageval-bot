import os
from dotenv import load_dotenv

load_dotenv()


def get_db_type():
    db_local = False
    is_db_local = os.environ.get("IS_DB_LOCAL")
    if is_db_local == "True":
        DB_LOCAL = True
    return db_local
