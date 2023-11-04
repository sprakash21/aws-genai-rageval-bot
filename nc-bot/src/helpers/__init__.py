import os
from src.helpers.env_utils import get_secret_info

os.environ["OPENAI_API_KEY"] = get_secret_info(os.environ.get("OPENAI_API_KEY_NAME"))[
    "token"
]
