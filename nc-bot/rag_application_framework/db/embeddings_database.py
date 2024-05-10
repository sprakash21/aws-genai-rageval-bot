from typing import Union

from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.vectorstores.pgvector import PGVector
from psycopg2.extensions import cursor as Cursor
from rag_application_framework.db.psycopg_connection_factory import (
    PsycopgConnectionFactory,
)


class EmbeddingsDatabase:
    """Uploads the unstructured pdf data into vectordb"""

    def __init__(
        self,
        vector_db: PsycopgConnectionFactory,
        collection_name: str,
        embeddings: Union[HuggingFaceEmbeddings, BedrockEmbeddings],
    ):
        self.vector_db = vector_db
        self.collection_name = collection_name
        self.embeddings = embeddings

    @property
    def cursor(self):
        return self.vector_db.make_connection().cursor()

    def execute_query_fetch_one(self, query: str, cursor: Union[Cursor, None] = None):
        if not cursor:
            _cursor = self.cursor
        else:
            _cursor = cursor

        _cursor.execute(query)
        result = _cursor.fetchone()

        if not cursor:
            _cursor.connection.close()

        return result

    def is_existing_table(
        self,
        cursor: Union[Cursor, None] = None,
    ) -> bool:
        query = """
                select exists(
                select * from information_schema.tables 
                where table_name='langchain_pg_embedding')
            """

        result = self.execute_query_fetch_one(query, cursor)

        if result:
            status = result[0]
            return bool(status)
        else:
            raise ValueError(f"Invalid result returned from database: {result}")

    def is_file_embedded(
        self,
        file_name: str,
        cursor: Union[Cursor, None] = None,
    ) -> bool:
        query = f"""
        select count(*) as counts
        from langchain_pg_embedding as embed
        where embed.cmetadata ->> 'source'='{file_name}'
        """

        result = self.execute_query_fetch_one(query, cursor)

        if result:
            counts = result[0]
            if counts > 0:
                return True
            else:
                return False

        raise ValueError(f"Invalid result returned from database: {result}")

    def clear_table(self):
        with self.cursor as cursor:
            if self.is_existing_table(cursor=cursor):
                """Truncates the embeddings table in the database."""
                query = f"TRUNCATE TABLE langchain_pg_embedding;"
                cursor.execute(query)
                cursor.connection.commit()

    def delete_documents_with_sources(self, sources: list[str], cursor=None):
        if not cursor:
            _cursor = self.cursor
        else:
            _cursor = cursor

        if self.is_existing_table(cursor=_cursor):
            id_placeholders = ','.join(['%s'] * len(sources))
            print(sources)
            query = f"""
            DELETE FROM langchain_pg_embedding as embed 
            WHERE embed.cmetadata ->> 'source' IN ({id_placeholders})
            """
            _cursor.execute(query, sources)
            _cursor.connection.commit()

        if not cursor:
            _cursor.connection.close()

    def save_as_embedding(
        self,
        documents: list[Document],
    ):
        """This function performs the required processing of the data for the given input
        file and puts that into the database.

        Args:
            fname (str): File name store in S3
            test_delete (bool, optional): _description_. Defaults to False.

        Returns:
            bool: Success or Failure of the process
        """

        # Short vs Long chunk

        document_unique_sources = list(
            set([doc.metadata["source"] for doc in documents])
        )

        with self.cursor as cursor:
            if self.is_existing_table(cursor):
                self.delete_documents_with_sources(sources=document_unique_sources)
                store = PGVector(
                    collection_name=self.collection_name,
                    connection_string=self.vector_db.get_connection_str(),
                    embedding_function=self.embeddings,
                )
                store.add_documents(documents)
            else:
                PGVector.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name=self.collection_name,
                    connection_string=self.vector_db.get_connection_str(),
                )
