import builtins
from constructs import Construct


class BaseConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        project_prefix: str,
        deploy_stage: str,
        deploy_region: str,
    ) -> None:
        super().__init__(scope, id)
        self.project_prefix = project_prefix
        self.deploy_stage = deploy_stage
        self.deploy_region = deploy_region
        self.construct_id = id

    @property
    def project_stage_prefix(self) -> str:
        return f"{self.project_prefix}-{self.deploy_stage}"

    @property
    def resource_prefix(self) -> str:
        return f"{self.project_stage_prefix}-{self.construct_id}"
    
    @property
    def region(self) -> str:
        return self.deploy_region
