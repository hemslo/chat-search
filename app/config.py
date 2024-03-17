import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN is not set in the environment variables")

CHAT_PROVIDER = os.getenv("CHAT_PROVIDER") or "openai"
DEBUG = os.getenv("DEBUG", "0") == "1"
VERBOSE = os.getenv("VERBOSE", "0") == "1"
DIGEST_PREFIX = os.getenv("DIGEST_PREFIX") or "digest"
ENABLE_FEEDBACK_ENDPOINT = os.getenv("ENABLE_FEEDBACK_ENDPOINT", "1") == "1"
ENABLE_PUBLIC_TRACE_LINK_ENDPOINT = (
    os.getenv("ENABLE_PUBLIC_TRACE_LINK_ENDPOINT", "1") == "1"
)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM") or 1536)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER") or "openai"
INDEX_NAME = os.getenv("INDEX_NAME") or "document"
INDEX_SCHEMA_PATH = (
    Path(os.getenv("INDEX_SCHEMA_PATH"))
    if os.getenv("INDEX_SCHEMA_PATH")
    else Path(os.path.dirname(__file__)) / "schema.yaml"
)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE") or 0)
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL") or "gemma"
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL") or "nomic-embed-text"
OLLAMA_URL = os.getenv("OLLAMA_URL") or "http://localhost:11434"
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL") or "gpt-3.5-turbo"
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL") or "text-embedding-3-small"
REDIS_URL = os.getenv("REDIS_URL") or "redis://localhost:6379/"
RETRIEVER_SEARCH_TYPE = os.getenv("RETRIEVER_SEARCH_TYPE") or "mmr"
RETRIEVER_SEARCH_KWARGS = (
    json.loads(os.getenv("RETRIEVER_SEARCH_KWARGS"))
    if os.getenv("RETRIEVER_SEARCH_KWARGS")
    else {
        "fetch_k": 20,
        "k": 4,
        "lambda_mult": 0.5,
    }
)
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME") or "chat-search"
PYROSCOPE_SERVER_ADDRESS = (
    os.getenv("PYROSCOPE_SERVER_ADDRESS") or "http://localhost:4040"
)
PYROSCOPE_BASIC_AUTH_USERNAME = os.getenv("PYROSCOPE_BASIC_AUTH_USERNAME") or ""
PYROSCOPE_BASIC_AUTH_PASSWORD = os.getenv("PYROSCOPE_BASIC_AUTH_PASSWORD") or ""

HEADERS_TO_SPLIT_ON = {
    h.strip() for h in (os.getenv("HEADERS_TO_SPLIT_ON") or "h1,h2,h3").split(",")
} & {"h1", "h2", "h3", "h4", "h5", "h6"}

TEXT_SPLIT_CHUNK_SIZE = int(os.getenv("TEXT_SPLIT_CHUNK_SIZE") or 4000)
TEXT_SPLIT_CHUNK_OVERLAP = int(os.getenv("TEXT_SPLIT_CHUNK_OVERLAP") or 200)

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
