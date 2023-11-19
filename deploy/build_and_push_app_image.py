import base64
import os
import subprocess
import boto3
from dataclasses import dataclass

from regex import F


@dataclass
class BuildPushResult:
    repository_name: str
    image_tag: str
    aws_region: str
    account_id: str
    full_image_url: str


class DockerImageBuilder:
    def __init__(
        self,
        dockerfile_path,
        context_dir_path,
        repo_name,
        image_tag,
        region,
        aws_profile=None,
    ):
        self.dockerfile_path = dockerfile_path
        self.context_dir_path = context_dir_path
        self.repo_name = repo_name
        self.image_tag = image_tag
        self.region = region
        self.aws_profile = aws_profile

        self.session = boto3.Session(
            region_name=self.region, profile_name=self.aws_profile
        )
        self.ecr_client = self.session.client("ecr", region_name=self.region)
        self.account_id = self._get_account_id()

    def _get_account_id(self):
        sts_client = self.session.client(
            "sts",
            region_name=self.region,
        )
        return sts_client.get_caller_identity()["Account"]

    def build_and_push(self):
        # Create ECR repository
        try:
            self.ecr_client.create_repository(repositoryName=self.repo_name)
            print(f"Repository {self.repo_name} created successfully.")
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            print(f"Repository {self.repo_name} already exists.")

        print(f"TAHA: {os.getcwd()}")

        # Build the Docker image
        build_command = f"docker build --platform linux/amd64 -t {self.repo_name} -f {self.dockerfile_path} {self.context_dir_path}"
        self._execute_docker_command(build_command)

        # Tag the image for ECR
        tag_command = f"docker tag {self.repo_name}:latest {self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.repo_name}:{self.image_tag}"
        self._execute_docker_command(tag_command)

        # Get ECR login details and login to ECR
        ecr_credentials = self.ecr_client.get_authorization_token()
        token = ecr_credentials["authorizationData"][0]["authorizationToken"]
        decoded_bytes = base64.b64decode(token)
        decoded_string = decoded_bytes.decode("utf-8")
        username, password = decoded_string.split(":")
        ecr_url = ecr_credentials["authorizationData"][0]["proxyEndpoint"]
        login_command = (
            f"docker login --username {username} --password {password} {ecr_url}"
        )
        self._execute_docker_command(login_command)

        # Push the image to ECR
        push_command = f"docker push {self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.repo_name}:{self.image_tag}"
        self._execute_docker_command(push_command)

        # Return the dataclass instance with the values
        full_image_url = f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.repo_name}:{self.image_tag}"
        return BuildPushResult(
            self.repo_name, self.image_tag, self.region, self.account_id, full_image_url
        )

    def _execute_docker_command(self, command) -> None:
        try:
            # Using subprocess.Popen to start the process
            with subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as process:
                # Reading the output line by line as it becomes available
                for line in process.stdout:
                    print(line, end="")

                # Wait for the process to terminate and get the exit code
                process.wait()

                # If the process exits with a non-zero code, raise an exception
                if process.returncode != 0:
                    # Read the stderr (if any) for error details
                    error_output = process.stderr.read()
                    raise subprocess.CalledProcessError(
                        returncode=process.returncode, cmd=command, output=error_output
                    )

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e.output}")
            raise
