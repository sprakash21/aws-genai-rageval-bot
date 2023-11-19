from abc import abstractmethod
from typing import Union
from langchain.embeddings import BedrockEmbeddings, HuggingFaceEmbeddings
from langchain.document_loaders.s3_file import S3FileLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_application_framework.db.embeddings_database import (
    EmbeddingsDatabase,
)


class FilesUploaderBase:
    def __init__(
        self,
        embeddings: Union[BedrockEmbeddings, HuggingFaceEmbeddings],
        embeddings_database: EmbeddingsDatabase,
    ) -> None:
        self.embeddings = embeddings
        self.embeddings_database = embeddings_database

    def upload_and_get_url(
        self,
        file_content: bytes,
        file_name: str,
    ) -> str:
        file_loader = self.upload_and_get_loader(
            file_content=file_content,
            file_name=file_name,
        )

        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1024, chunk_overlap=50
        )

        documents = file_loader.load_and_split(
            text_splitter=text_splitter,
        )

        self.embeddings_database.save_as_embedding(
            documents=documents,
        )

        return self.get_url(file_name)

    @abstractmethod
    def get_url(self, file_name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def upload_and_get_loader(
        self,
        file_content: bytes,
        file_name: str,
    ) -> Union[S3FileLoader, UnstructuredFileLoader]:
        raise NotImplementedError()

    def clear_context_db(self):
        self.embeddings_database.clear_table()
        self.clear_store()

    @abstractmethod
    def clear_store(self):
        raise NotImplementedError()
