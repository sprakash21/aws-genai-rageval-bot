import os
from logging_config import get_logger

logger = get_logger(__name__)


def store_file(s3_key: str, stream_body: str) -> str:
    """
    Store the obtained StreamingBody from S3 and store it locally on the defined
    input location as the same name filename as per name in S3.
    >>> from file_utils import store_file
    >>> store_file(s3_key="data/some_file")
    s3_key:str: The S3 Key location of the excel sheet is passed.
    stream_body:str: The streaming body obtained from S3.
    """
    try:
        s3_arr = s3_key.split("/")
        s3_fname = s3_arr.pop(-1)
        s3_dir = "/".join(val for val in s3_arr)
        os.makedirs(s3_dir, exist_ok=True)
        local_fname = os.path.join(s3_dir, s3_fname)
        logger.info("The local file name is store in %s", local_fname)
        with open(local_fname, "wb") as f_obj:
            # File Objects storing.
            f_obj.write(stream_body.read())
        return local_fname
    except IOError as e:
        # Raise this.
        raise e
