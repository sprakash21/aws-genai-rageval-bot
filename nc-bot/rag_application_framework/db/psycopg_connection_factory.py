import psycopg2
from langchain.vectorstores.pgvector import PGVector
from psycopg2.extensions import connection


class PsycopgConnectionFactory:
    """Uploads the unstructured pdf data into vectordb"""

    def __init__(
        self, host: str, port: int, database_name: str, username: str, password: str
    ):
        self.host = host
        self.port = port
        self.database_name = database_name
        self.username = username
        self.password = password

    def get_connection_str(self) -> str:
        """Generates the Connection String required to connect to the Database

        Returns:
            _type_: _description_
        """

        CONNECTION_STRING = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=self.host,
            port=self.port,
            database=self.database_name,
            user=self.username,
            password=self.password,
        )
        return CONNECTION_STRING

    def make_connection(self) -> connection:
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.database_name,
            user=self.username,
            password=self.password,
        )
        return conn
