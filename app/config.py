import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

INDEX_SCHEMA_PATH = Path(os.path.dirname(__file__)) / "schema.yaml"

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

INDEX_NAME = "document"

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN is not set in the environment variables")
