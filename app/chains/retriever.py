from typing import List

from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.retrievers import RetrieverLike
from langchain_core.runnables import RunnableLambda

from app import config
from app.dependencies.redis import get_redis
from app.dependencies.redis_fulltext_retriever import RedisFulltextRetriever


def top_k(docs: List[Document]) -> List[Document]:
    return docs[: config.RETRIEVER_SEARCH_K]


def build_hybrid_retriever_chain() -> RetrieverLike:
    redis = get_redis()

    fulltext_retriever = RedisFulltextRetriever.from_vectorstore(
        vectorstore=redis,
        k=config.FULLTEXT_RETRIEVER_SEARCH_K,
    ).with_config(run_name="fulltext_retriever")

    vectorstore_retriever = redis.as_retriever(
        search_type=config.VECTORSTORE_RETRIEVER_SEARCH_TYPE,
        search_kwargs=config.VECTORSTORE_RETRIEVER_SEARCH_KWARGS,
    ).with_config(run_name="vectorstore_retriever")

    ensemble_retriever = EnsembleRetriever(
        retrievers=[fulltext_retriever, vectorstore_retriever],
        weights=[config.FULLTEXT_RETRIEVER_WEIGHT, config.VECTORSTORE_RETRIEVER_WEIGHT],
    )

    return ensemble_retriever | RunnableLambda(top_k)


retriever_chain = build_hybrid_retriever_chain()
