import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose

load_dotenv()

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN is not set in the environment variables")

CHAT_PROVIDER = os.environ.get("CHAT_PROVIDER", "openai")
DEBUG = os.getenv("DEBUG", "0") == "1"
VERBOSE = os.getenv("VERBOSE", "0") == "1"
EMBEDDING_DIM = int(os.environ.get("EMBEDDING_DIM", 1536))
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "openai")
INDEX_NAME = "document"
INDEX_SCHEMA_PATH = Path(os.path.dirname(__file__)) / "schema.yaml"
OLLAMA_CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "llama2")
OLLAMA_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "llama2")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-3.5-turbo-0125")
OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/")

REPHRASE_PROMPT = (
    os.getenv("REPHRASE_PROMPT")
    or """\
Given the following conversation and a follow up question, \
rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {input}
Standalone Question:
"""
)

RETRIEVAL_QA_CHAT_SYSTEM_PROMPT = (
    os.getenv("RETRIEVAL_QA_CHAT_SYSTEM_PROMPT")
    or """\
You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.

<context>
{context}
</context>
"""
)

set_debug(DEBUG)
set_verbose(VERBOSE)
