from aws_cdk import Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codecommit as codecommit
from aws_cdk import aws_ecr as ecr
from aws_cdk.pipelines import CodeBuildStep, CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from deploy_stage import ApplicationDeploymentBuilder, ApplicationDeployStage


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_prefix: str,
        deploy_stage: str,
        docker_image_name: str,
        code_commit_repo_name: str,
        app_deployment_builder: ApplicationDeploymentBuilder,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        self.scope = scope

        prefix = f"{project_prefix}-{deploy_stage}"

        self.ecr_repo_name = f"{prefix}-ecr-repo"

        # Define the ECR repository
        repo = ecr.Repository(self, "ecr-repo", repository_name=self.ecr_repo_name)

        code_repo = CodePipelineSource.code_commit(
            codecommit.Repository.from_repository_name(
                scope=self, id="repo", repository_name=code_commit_repo_name
            ),
            "main",
        )

        # Grant the CodeBuild project permissions to the ECR repository

        pipeline_deploy_stage = ApplicationDeployStage(
            scope=self,
            id="deployment-stage",
            app_deployment_builder=app_deployment_builder,
        )

        # Create the pipeline
        pipeline = CodePipeline(
            self,
            f"{prefix}-pipeline",
            pipeline_name=f"{prefix}-pipeline",
            synth=ShellStep(
                "Synth",
                input=code_repo,
                commands=[
                    "cd deploy",
                    "npm install -g aws-cdk",
                    "python -m pip install -r requirements.txt",
                    "cdk synth",
                ],
            ),
        )

        app_deployment = pipeline.add_stage(pipeline_deploy_stage)

        code_build_step = CodeBuildStep(
            "CodeBuild",
            project_name=f"{prefix}-cb-project",
            input=code_repo,
            commands=[
                f"echo Logging into Amazon ECR in region {self.region}...",
                f"$(aws ecr get-login --no-include-email --region {self.region})",
                "echo Build started on $(date)",
                "echo Building the Docker image...",
                f"docker build -t {docker_image_name} .",
                f"docker tag {docker_image_name}:latest {repo.repository_uri}:latest",
                "echo Build completed on $(date)",
                f"docker push {repo.repository_uri}:latest",
                "echo Done!",
            ],
            build_environment=codebuild.BuildEnvironment(
                privileged=True,
                build_image=codebuild.LinuxBuildImage.STANDARD_4_0,
            ),
        )

        app_deployment.add_pre(code_build_step)
