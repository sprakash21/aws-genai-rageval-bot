from abc import abstractmethod
from typing import Optional, Union
from attr import dataclass
from langchain.embeddings import BedrockEmbeddings, HuggingFaceEmbeddings
from langchain.document_loaders.s3_file import S3FileLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_application_framework.db.embeddings_database import (
    EmbeddingsDatabase,
)
from langchain.schema.document import Document
from rag_application_framework.logging.logging import Logging

logger = Logging.get_logger(__name__)


@dataclass
class FileUpload:
    file_content: bytes
    file_name: str
    custom_metadata: Optional[dict] = None


@dataclass
class UploadedFile:
    file_name: str
    url: Optional[str] = None
    error: Optional[Exception] = None


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
        list_of_files: list[FileUpload],
    ) -> list[UploadedFile]:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"], chunk_size=1024, chunk_overlap=50
        )

        all_documents: list[Document] = []
        result: list[UploadedFile] = []

        for file in list_of_files:
            try:
                file_content = file.file_content
                file_name = file.file_name
                custom_metadata = file.custom_metadata or {}

                file_loader = self.store_file_and_get_loader(
                    file_content=file_content,
                    file_name=file_name,
                )

                documents = file_loader.load_and_split(
                    text_splitter=text_splitter,
                )

                for document in documents:
                    document.metadata = {
                        **document.metadata,
                        **custom_metadata,
                    }
                all_documents.extend(documents)
                result.append(
                    UploadedFile(
                        file_name=file.file_name,
                        url=self.get_url(file_name),
                    )
                )
            except Exception as e:
                logger.error(e)
                result.append(
                    UploadedFile(
                        file_name=file.file_name,
                        error=e,
                    )
                )

        self.embeddings_database.save_as_embedding(
            documents=all_documents,
        )

        return result

    @abstractmethod
    def get_url(self, file_name: str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def store_file_and_get_loader(
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
