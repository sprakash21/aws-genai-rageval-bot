from boto3.session import Session
from langchain.document_loaders.s3_file import S3FileLoader
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.embeddings import BedrockEmbeddings, HuggingFaceEmbeddings
from rag_application_framework.aws.aws_client_factory import AwsClientFactory
from rag_application_framework.aws.s3_api import S3Api
from rag_application_framework.db.embeddings_database import EmbeddingsDatabase
from rag_application_framework.modules.file_uploader.file_uploader import (
    FilesUploaderBase,
)


from typing import Union


class S3FilesUploader(FilesUploaderBase):
    def __init__(
        self,
        embeddings: Union[BedrockEmbeddings, HuggingFaceEmbeddings],
        embeddings_database: EmbeddingsDatabase,
        bucket_name: str,
        boto3_session: Session,
    ) -> None:
        super().__init__(
            embeddings=embeddings,
            embeddings_database=embeddings_database,
        )
        self.bucket_name = bucket_name
        self.boto3_session = boto3_session

    def store_file_and_get_loader(
        self,
        file_content: bytes,
        file_name: str,
    ) -> S3FileLoader:
        s3_api = AwsClientFactory.build_from_boto_session(
            session=self.boto3_session, service_api_type=S3Api
        )

        s3_api.put_object(
            bucket_name=self.bucket_name,
            object_key=file_name,
            data=file_content,
        )

        file_loader = S3FileLoader(
            bucket=self.bucket_name,
            key=file_name,
            region_name=s3_api.client.meta.region_name,
        )

        return file_loader

    def clear_store(self):
        s3_api = AwsClientFactory.build_from_boto_session(
            session=self.boto3_session, service_api_type=S3Api
        )
        s3_api.empty_bucket(self.bucket_name)

    def get_url(self, file_name: str) -> str:
        s3_api = AwsClientFactory.build_from_boto_session(
            session=self.boto3_session, service_api_type=S3Api
        )
        return s3_api.generate_presigned_url(self.bucket_name, file_name)
