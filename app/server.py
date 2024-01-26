#!/usr/bin/env python
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from langchain_openai import ChatOpenAI
from langserve import add_routes

from app.dependencies import verify_auth_token
from app.routers import ingest

load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    ChatOpenAI(),
    path="/openai",
)

app.include_router(
    ingest.router,
    dependencies=[Depends(verify_auth_token)],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
