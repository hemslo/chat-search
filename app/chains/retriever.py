from typing import List

from langchain.chains.query_constructor.base import (
    AttributeInfo,
    load_query_constructor_runnable,
)
from langchain.chains.query_constructor.ir import StructuredQuery
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.self_query.base import (
    QUERY_CONSTRUCTOR_RUN_NAME,
    SelfQueryRetriever,
)
from langchain_community.query_constructors.redis import RedisTranslator
from langchain_core.documents import Document
from langchain_core.retrievers import RetrieverLike
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

from app import config
from app.dependencies.llm import get_llm
from app.dependencies.redis import get_redis
from app.dependencies.redis_fulltext_retriever import RedisFulltextRetriever

METADATA_FIELD_INFO = [
    AttributeInfo(
        name="title",
        description="Title of the document",
        type="string",
    ),
    AttributeInfo(
        name="description",
        description="Description of the document",
        type="string",
    ),
    AttributeInfo(
        name="language",
        description="Language of the document",
        type="string",
    ),
    AttributeInfo(
        name="source",
        description="Source of the document",
        type="string",
    ),
]


def top_k(docs: List[Document]) -> List[Document]:
    return docs[: config.RETRIEVER_SEARCH_K]


def build_fulltext_retriever_chain() -> RetrieverLike:
    redis = get_redis()

    if not config.FULLTEXT_RETRIEVER_SELF_QUERY:
        return RedisFulltextRetriever.from_vectorstore(
            vectorstore=redis,
            k=config.FULLTEXT_RETRIEVER_SEARCH_K,
        ).with_config(run_name="fulltext_retriever")

    structured_query_translator = RedisTranslator.from_vectorstore(redis)
    query_constructor = load_query_constructor_runnable(
        llm=get_llm(),
        document_contents=config.DOCUMENT_CONTENT_DESCRIPTION,
        attribute_info=METADATA_FIELD_INFO,
        allowed_operators=structured_query_translator.allowed_operators,
        allowed_comparators=structured_query_translator.allowed_comparators,
        examples=config.RETRIEVER_SELF_QUERY_EXAMPLES,
    ).with_config(run_name=QUERY_CONSTRUCTOR_RUN_NAME)

    def build_fulltext_retriever(structured_query: StructuredQuery) -> RetrieverLike:
        new_query, new_kwargs = structured_query_translator.visit_structured_query(
            structured_query
        )
        fulltext_retriever = RedisFulltextRetriever.from_vectorstore(
            vectorstore=redis,
            k=config.FULLTEXT_RETRIEVER_SEARCH_K,
            filter=new_kwargs.get("filter"),
        ).with_config(run_name="fulltext_retriever")

        def query(_: str) -> str:
            return new_query

        return RunnableLambda(query) | fulltext_retriever

    return (
        RunnableParallel({"query": RunnablePassthrough()})
        | query_constructor
        | RunnableLambda(build_fulltext_retriever)
    )


def build_vectorstore_retriever_chain() -> RetrieverLike:
    redis = get_redis()
    if not config.VECTORSTORE_RETRIEVER_SELF_QUERY:
        return redis.as_retriever(
            search_type=config.VECTORSTORE_RETRIEVER_SEARCH_TYPE,
            search_kwargs=config.VECTORSTORE_RETRIEVER_SEARCH_KWARGS,
        ).with_config(run_name="vectorstore_retriever")

    return SelfQueryRetriever.from_llm(
        llm=get_llm(),
        vectorstore=redis,
        document_contents=config.DOCUMENT_CONTENT_DESCRIPTION,
        metadata_field_info=METADATA_FIELD_INFO,
        use_original_query=True,
        chain_kwargs={
            "examples": config.RETRIEVER_SELF_QUERY_EXAMPLES,
        },
        search_type=config.VECTORSTORE_RETRIEVER_SEARCH_TYPE,
        search_kwargs=config.VECTORSTORE_RETRIEVER_SEARCH_KWARGS,
        verbose=config.VERBOSE,
    ).with_config(run_name="vectorstore_retriever")


def build_hybrid_retriever_chain() -> RetrieverLike:
    fulltext_retriever = build_fulltext_retriever_chain()
    vectorstore_retriever = build_vectorstore_retriever_chain()
    ensemble_retriever = EnsembleRetriever(
        retrievers=[fulltext_retriever, vectorstore_retriever],
        weights=[config.FULLTEXT_RETRIEVER_WEIGHT, config.VECTORSTORE_RETRIEVER_WEIGHT],
    )
    return ensemble_retriever | RunnableLambda(top_k)


retriever_chain = build_hybrid_retriever_chain()
