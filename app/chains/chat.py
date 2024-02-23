from collections.abc import Sequence

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    FunctionMessage,
    ChatMessage,
    ToolMessage,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.prompts.prompt import PromptTemplate
from pydantic import Field, BaseModel

from app import config
from app.dependencies.llm import get_llm
from app.dependencies.redis import get_redis


def build_chat_chain():
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
    return create_retrieval_chain(retriever_chain, combine_docs_chain)


class Input(BaseModel):
    chat_history: Sequence[
        HumanMessage
        | AIMessage
        | SystemMessage
        | FunctionMessage
        | ChatMessage
        | ToolMessage
    ] = Field(
        ...,
        extra={
            "widget": {"type": "chat", "input": "input", "output": "answer"},
        },
    )
    input: str


class Output(BaseModel):
    answer: str
    context: Sequence[Document]


chat_chain = build_chat_chain().with_types(input_type=Input, output_type=Output)
