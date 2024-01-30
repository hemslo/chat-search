from operator import itemgetter
from typing import List, Tuple

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, format_document
from langchain_core.runnables import (
    RunnableParallel,
)
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langserve import CustomUserType
from pydantic import Field

from app import config
from app.dependencies.redis import get_redis

llm = ChatOpenAI(
    model=config.OPENAI_CHAT_MODEL,
    temperature=0,
)

retriever = get_redis().as_retriever(search_type="mmr")


REPHRASE_TEMPLATE = """\
Given the following conversation and a follow up question, \
rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:
"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(REPHRASE_TEMPLATE)

ANSWER_TEMPLATE = """\
Use the following pieces of context to answer the question at the end. \
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}

Helpful Answer:
"""

ANSWER_PROMPT = ChatPromptTemplate.from_template(ANSWER_TEMPLATE)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")


def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


class ChatHistory(CustomUserType):
    chat_history: List[Tuple[str, str]] = Field(
        ...,
        examples=[[("human input", "ai response")]],
        extra={"widget": {"type": "chat", "input": "question", "output": "answer"}},
    )
    question: str


def _format_chat_history(chat_history: ChatHistory) -> List[BaseMessage]:
    messages = []
    for human, ai in chat_history.chat_history:
        messages.append(HumanMessage(content=human))
        messages.append(AIMessage(content=ai))
    return messages


_inputs = RunnableParallel(
    standalone_question={
        "chat_history": _format_chat_history,
        "question": lambda x: x.question,
    }
    | CONDENSE_QUESTION_PROMPT
    | llm
    | StrOutputParser(),
)

_retrieved_documents = {
    "docs": itemgetter("standalone_question") | retriever,
    "question": itemgetter("standalone_question"),
}

_final_inputs = {
    "context": lambda x: _combine_documents(x["docs"]),
    "question": itemgetter("question"),
}

_answer = {
    "answer": _final_inputs | ANSWER_PROMPT | llm | StrOutputParser(),
    "docs": itemgetter("docs"),
}


_conversational_qa_chain = _inputs | _retrieved_documents | _answer

chat_chain = _conversational_qa_chain.with_types(input_type=ChatHistory)
