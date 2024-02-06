import os
from typing import Annotated

from fastapi import Depends
from langchain_community.vectorstores.redis import Redis

from app import config
from app.dependencies.embeddings import get_embeddings

rds = Redis(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/"),
    index_name=config.INDEX_NAME,
    embedding=get_embeddings(),
    index_schema=config.INDEX_SCHEMA_PATH,
)

rds._create_index_if_not_exist(config.EMBEDDING_DIM)


def get_redis() -> Redis:
    return rds


RedisDep = Annotated[Redis, Depends(get_redis)]
