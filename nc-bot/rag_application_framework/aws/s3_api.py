from rag_application_framework.aws.base_aws_client import BaseAwsClient
from rag_application_framework.logging.logging import Logging
from rag_application_framework.aws.base_aws_client import (
    MetaClass,
    BaseAwsClient,
    AwsServiceNameClassProperty,
)

logger = Logging.get_logger(__name__)


class S3Api(BaseAwsClient, metaclass=MetaClass):
    service_name = AwsServiceNameClassProperty("s3")

    def get_object(self, bucket_name: str, object_key: str):
        """Retrieves an object from an S3 bucket."""
        try:
            response = self._client.get_object(Bucket=bucket_name, Key=object_key)
            return response
        except Exception as e:
            logger.error(f"Error getting object: {e}")
            raise

    def list_objects(self, bucket_name: str):
        """Lists all objects in a specified S3 bucket."""
        try:
            response = self._client.list_objects_v2(Bucket=bucket_name)
            return response.get("Contents", [])
        except Exception as e:
            logger.error(f"Error listing objects: {e}")
            raise

    def put_object(self, bucket_name: str, object_key: str, data: bytes):
        """Uploads an object to an S3 bucket."""
        try:
            self._client.put_object(Bucket=bucket_name, Key=object_key, Body=data)
        except Exception as e:
            logger.error(f"Error putting object: {e}")
            raise

    def empty_bucket(self, bucket_name: str):
        """Empties a bucket by deleting all objects within it."""
        objects = self.list_objects(bucket_name)
        for obj in objects:
            self.delete_object(bucket_name, obj["Key"])

    def delete_object(self, bucket_name: str, object_key: str):
        """Deletes a specific object from an S3 bucket."""
        try:
            self._client.delete_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            logger.error(f"Error deleting object: {e}")
            raise

    def generate_presigned_url(self, bucket_name: str, fname: str) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": fname},
            ExpiresIn=600,
        )
