from langchain_core.embeddings import Embeddings

from app import config


def _get_embeddings() -> Embeddings:
    match config.EMBEDDING_PROVIDER:
        case "openai":
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                model=config.OPENAI_EMBEDDING_MODEL,
            )
        case "ollama":
            from langchain_community.embeddings import OllamaEmbeddings

            return OllamaEmbeddings(
                model=config.OLLAMA_EMBEDDING_MODEL,
                base_url=config.OLLAMA_URL,
            )
        case _:
            raise ValueError(f"Unknown embedding provider: {config.EMBEDDING_PROVIDER}")


embeddings = _get_embeddings()


def get_embeddings() -> Embeddings:
    return embeddings
