from enum import Enum

class InferenceEngine(Enum):
    LOCAL = 0
    SAGEMAKER = 1
    BEDROCK = 2