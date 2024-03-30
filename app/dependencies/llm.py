from langchain_core.language_models import BaseChatModel

from app import config


def _get_llm() -> BaseChatModel:
    match config.CHAT_PROVIDER:
        case "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=config.OPENAI_CHAT_MODEL,
                temperature=config.LLM_TEMPERATURE,
                openai_api_base=config.OPENAI_API_BASE,
                openai_api_key=config.OPENAI_API_KEY,
            )
        case "ollama":
            from langchain_community.chat_models.ollama import ChatOllama

            return ChatOllama(
                model=config.OLLAMA_CHAT_MODEL,
                base_url=config.OLLAMA_URL,
                temperature=config.LLM_TEMPERATURE,
            )
        case _:
            raise ValueError(f"Unknown chat provider: {config.CHAT_PROVIDER}")


llm = _get_llm()


def get_llm() -> BaseChatModel:
    return llm
