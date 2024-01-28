#!/usr/bin/env python
from fastapi import FastAPI, Depends
from langchain_openai import ChatOpenAI
from langserve import add_routes

from app.dependencies.auth_token import verify_auth_token
from app.routers import ingest

app = FastAPI(
    title="Chat Search",
    version="1.0",
    description="Chat Search for documents",
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
