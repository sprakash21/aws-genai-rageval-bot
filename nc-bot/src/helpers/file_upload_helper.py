import os
import boto3
from botocore.exceptions import ClientError
from src.helpers.file_utils import store_file
from logging_config import get_logger

logger = get_logger(__name__)

class S3FileUpload:
    def __init__(self):
        self.client = boto3.Session(profile_name=os.environ.get("AWS_PROFILE")).client("s3")
        self.bucket = os.environ.get("BUCKET_NAME")

    def get_object(self, key: str):
        """
        Gets an object from S3 for the provided provided prefix and file name.

        >>> from helpers.s3_helpers import S3Operations
        >>> client = S3operations()
        >>> BytesIO = client.get_object(key="test.png")

        :key: The pdf to get once being stored.
        return Bytes IO of the data. Needs some reading with it.
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # The response to the request is successful.
                logger.info("The request is successful.")
                # Create the required directories for the key to be downloaded.
                l_fname = store_file(s3_key=key, stream_body=response["Body"])
                logger.info("The file is successfully stored at %s location", l_fname)
                return l_fname
            else:
                logger.error("There has been some error with the request")
                return ""
        except ClientError as e:
            logger.error("There has been an exception with boto3 connections %s", e)
            return ""
        except IOError as exc:
            logger.error("There has been exception with the file storage %s", exc)
            return ""

    def list_objects(self, prefix: str):
        """
        Lists all objects under a specified prefix at S3.

        >>> from helpers.s3_helpers import S3Operations
        >>> client = S3operations()
        >>> client.list_objects(prefix="")

        :prefix: bucket prefix to lookup for obtaining the file.
        :fname: File name

        """
        kwargs = {"Bucket": self.bucket, "Prefix": prefix, "MaxKeys": 1000}
        try:
            response = self.client.list_objects_v2(**kwargs)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # The response to the request is successful.
                logger.info("The request is successful.")
                if "Contents" in response.keys():
                    return [val["Key"] for val in response["Contents"]]
                logger.info("There is no content obtained for the prefix")
                return response
            else:
                logger.info("There has been some error with the request")
                return False
        except ClientError as e:
            # Raise
            logger.error("There has been an exception with client request %s", e)
            return False

    def delete_object(self, key: str):
        """
        Deletes a file object at the specified prefix at S3.

        >>> from helpers.s3_helpers import S3Operations
        >>> client = S3operations()
        >>> client.delete_object(key="test.png")
        :key: bucket prefix to lookup for obtaining the file.
        """
        try:
            response = self.client.delete_object(Bucket=self.bucket, Key=key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("The specified key-%s is deleted at S3", key)
                return True

        except ClientError as e:
            logger.error("There has been an error with the boto3 request %s", e)
            return False

    def put_object(self, f_body: str, object_name):
        """
        Puts an object to S3.
        >>> from helpers.s3_helpers import S3Operations
        >>> client = S3operations()
        >>> client.put_object(f_body="string_body", object_name="prefix_name")
        """
        try:
            self.client.put_object(ACL='public-read', Bucket=self.bucket, Body=f_body, ContentType="application/pdf", Key=object_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True
