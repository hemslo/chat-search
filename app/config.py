import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN is not set in the environment variables")

CHAT_PROVIDER = os.environ.get("CHAT_PROVIDER", "openai")
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", 1536))
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "openai")
INDEX_NAME = "document"
INDEX_SCHEMA_PATH = Path(os.path.dirname(__file__)) / "schema.yaml"
OLLAMA_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "llama2")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "llama2")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-3.5-turbo-1106")
OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")
