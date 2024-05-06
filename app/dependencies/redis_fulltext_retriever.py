from typing import List, Self

from langchain_community.vectorstores.redis import Redis as RedisVectorStore
from langchain_community.vectorstores.redis.filters import RedisFilterExpression
from langchain_community.vectorstores.redis.schema import RedisModel
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from redis import Redis
from redis.commands.search.document import Document as RedisDocument
from redis.commands.search.query import Query


class RedisFulltextRetriever(BaseRetriever):
    client: Redis
    schema_model: RedisModel
    index_name: str
    k: int = 4
    filter: RedisFilterExpression | None = None

    def _build_document(self, doc: RedisDocument) -> Document:
        page_content = getattr(doc, self.schema_model.content_key)
        metadata = {
            "id": doc.id,
        } | {k: getattr(doc, k, None) for k in self.schema_model.metadata_keys}
        return Document(page_content=page_content, metadata=metadata)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        docs = self.client.ft(self.index_name).search(self._prepare_query(query)).docs
        return [self._build_document(doc) for doc in docs]

    def _prepare_query(self, query: str) -> Query:
        return_fields = self.schema_model.metadata_keys + [
            self.schema_model.content_key
        ]
        query_string = query if self.filter is None else f"({self.filter}) ({query})"
        return (
            Query(query_string)
            .return_fields(*return_fields)
            .paging(0, self.k)
            .dialect(2)
        )

    @classmethod
    def from_vectorstore(
        cls,
        vectorstore: RedisVectorStore,
        k: int = 4,
        filter: RedisFilterExpression | None = None,
    ) -> Self:
        return cls(
            client=vectorstore.client,
            schema_model=vectorstore._schema,
            index_name=vectorstore.index_name,
            k=k,
            filter=filter,
        )
