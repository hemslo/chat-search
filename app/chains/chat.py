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

from app.dependencies.llm import get_llm
from app.dependencies.redis import get_redis

RETRIEVAL_QA_CHAT_SYSTEM_PROMPT = """\
Answer any questions based solely on the context below:

<context>
{context}
</context>
"""

REPHRASE_PROMPT = """\
Given the following conversation and a follow up question, \
rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {input}
Standalone Question:
"""


def build_chat_chain():
    llm = get_llm()

    retriever = get_redis().as_retriever(
        search_type="mmr",
        search_kwargs={
            "fetch_k": 20,
            "k": 3,
            "lambda_mult": 0.5,
        },
    )

    rephrase_prompt = PromptTemplate.from_template(REPHRASE_PROMPT)

    retriever_chain = create_history_aware_retriever(
        llm,
        retriever,
        rephrase_prompt,
    )

    retrieval_qa_chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                RETRIEVAL_QA_CHAT_SYSTEM_PROMPT,
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
