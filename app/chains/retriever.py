from app.dependencies.redis import get_redis
from app.dependencies.redis_fulltext_retriever import RedisFulltextRetriever


def build_retriever() -> RedisFulltextRetriever:
    redis = get_redis()
    return RedisFulltextRetriever.from_vectorstore(redis)


retriever = build_retriever()
