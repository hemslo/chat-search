from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app import config
from app.dependencies.redis import get_redis

llm = ChatOpenAI(
    model=config.OPENAI_CHAT_MODEL,
    streaming=True,
    temperature=0,
)

retriever = get_redis().as_retriever(search_type="mmr")

template = """\
Use the following pieces of context to answer the question at the end. \
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}

Helpful Answer:
"""

prompt = ChatPromptTemplate.from_template(template)


class Question(BaseModel):
    __root__: str


chat_chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | llm
    | StrOutputParser()
).with_types(input_type=Question)
