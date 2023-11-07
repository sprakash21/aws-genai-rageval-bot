import json
import boto3
import botocore
import os


def get_secret_info(secret_name):
    """Get the secret information based on the secret name

    Args:
        secret_name (str): The name of secret to pass

    Returns:
        dict: Dictionary of secret information
    """

    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def get_secret_info_json(secret_name):
    """Get the secret information based on the secret name

    Args:
        secret_name (str): The name of secret to pass

    Returns:
        dict: Dictionary of secret information
    """

    secret_string = get_secret_info(secret_name)
    return json.loads(secret_string)


def get_ssm_parameter_value(parameter_name):
    """Gets the information from SSM parameter store

    Args:
        parameter_name (str): Parameter Name

    Returns:
        _type_: _description_
    """
    try:
        client = boto3.client("ssm")
        response = client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response["Parameter"]["Value"]
    except botocore.exceptions.ClientError as exc:
        print("There has been an error while obtaining ssm information", exc)
        return None
