from langchain.document_loaders.s3_file import S3FileLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from rag_application_framework.db.embeddings_database import EmbeddingsDatabase
from rag_application_framework.modules.file_uploader.file_uploader import (
    FilesUploaderBase,
)


import os
from typing import Union


class FileSystemFilesUploader(FilesUploaderBase):
    def __init__(
        self,
        embeddings: Union[BedrockEmbeddings, HuggingFaceEmbeddings],
        embeddings_database: EmbeddingsDatabase,
        folder_path: str,
    ) -> None:
        super().__init__(
            embeddings=embeddings,
            embeddings_database=embeddings_database,
        )
        self.folder_path = folder_path

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def store_file_and_get_loader(
        self,
        file_content: bytes,
        file_name: str,
    ) -> Union[S3FileLoader, UnstructuredFileLoader]:
        file_path = f"{self.folder_path}/{file_name}"
        with open(file_path, "wb") as f:
            f.write(file_content)

        file_loader = UnstructuredFileLoader(
            file_path=file_path,
        )

        return file_loader

    def clear_store(self):
        for file in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)

    def get_url(self, file_name: str) -> str:
        absolute_path = self.folder_path

        return f"file:/{absolute_path}/{file_name}"
