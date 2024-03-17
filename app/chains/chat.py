from collections.abc import AsyncIterator
from typing import TypedDict

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.prompts.prompt import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, Runnable
from pydantic import BaseModel

from app import config
from app.dependencies.llm import get_llm
from app.dependencies.redis import get_redis


class InputChat(BaseModel):
    messages: list[HumanMessage | AIMessage | SystemMessage]


class InputDict(TypedDict):
    messages: list[HumanMessage | AIMessage | SystemMessage]


def _get_chat_history(
    input_chat: InputDict,
) -> list[HumanMessage | AIMessage | SystemMessage]:
    return input_chat["messages"][:-1]


def _get_input(
    input_chat: InputDict,
) -> str:
    return input_chat["messages"][-1].content


async def _build_output(results: AsyncIterator[dict]) -> AsyncIterator[str]:
    async for result in results:
        match result:
            case {"answer": answer}:
                yield answer


def build_chat_chain() -> Runnable:
    llm = get_llm()

    retriever = get_redis().as_retriever(
        search_type=config.RETRIEVER_SEARCH_TYPE,
        search_kwargs=config.RETRIEVER_SEARCH_KWARGS,
    )

    rephrase_prompt = PromptTemplate.from_template(config.REPHRASE_PROMPT)

    retriever_chain = create_history_aware_retriever(
        llm,
        retriever,
        rephrase_prompt,
    )

    retrieval_qa_chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                config.RETRIEVAL_QA_CHAT_SYSTEM_PROMPT,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "user",
                "{input}",
            ),
        ]
    )

    combine_docs_chain = create_stuff_documents_chain(
        llm,
        retrieval_qa_chat_prompt,
    )

    return (
        RunnableParallel(
            {
                "chat_history": RunnableLambda(_get_chat_history),
                "input": RunnableLambda(_get_input),
            }
        )
        | create_retrieval_chain(
            retriever_chain,
            combine_docs_chain,
        )
        | _build_output
    )


chat_chain = build_chat_chain().with_types(input_type=InputChat)
