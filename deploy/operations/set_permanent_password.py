import string
import boto3
import argparse
import secrets


def _generate_password(length: int = 12) -> str:
    # Define password character requirements
    alphabet = string.ascii_letters + string.digits + string.punctuation

    # Securely generate a random password
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))

        # Ensure password meets requirements: at least one uppercase, lowercase, digit, and special character
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            break

    return password


def handler(config: dict) -> dict:
    session = boto3.Session(region_name=config["region"])
    client = session.client('cognito-idp')
    password = _generate_password()
    # Set user password
    client.admin_set_user_password(
        UserPoolId=config["user_pool_id"],
        Username=config["username"],
        Password=password,
        Permanent=True  # Makes the password permanent
    )
    # Add to SecretsManager or update

    return {"status": "password set successfully", "password": password}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set user password permanently",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-u", "--username", type=str, help="username")
    parser.add_argument("-r", "--region", type=str, required=False, help="region of the AWS Account")
    parser.add_argument("-pid", "--user_pool_id", type=str, help="User pool id of Amazon Cognito")
    args = parser.parse_args()
    configs = vars(args)
    status = handler(configs)
    print(status)
