#!/usr/bin/env python
from fastapi import Depends, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from langserve import add_routes

from app import config
from app.chains.chat import chat_chain
from app.chains.retriever import retriever_chain
from app.dependencies.auth_token import verify_auth_token
from app.routers import ingest

if config.PYROSCOPE_ENABLED:
    import pyroscope

    pyroscope.configure(
        application_name=config.SERVICE_NAME,
        server_address=config.PYROSCOPE_SERVER_ADDRESS,
        basic_auth_username=config.PYROSCOPE_BASIC_AUTH_USERNAME,
        basic_auth_password=config.PYROSCOPE_BASIC_AUTH_PASSWORD,
    )

app = FastAPI(
    title="Chat Search",
    version="1.0",
    description="Chat Search for documents",
)

add_routes(
    app,
    chat_chain,
    path="/chat",
    enable_feedback_endpoint=config.ENABLE_FEEDBACK_ENDPOINT,
    enable_public_trace_link_endpoint=config.ENABLE_PUBLIC_TRACE_LINK_ENDPOINT,
    playground_type="chat",
)

add_routes(
    app,
    retriever_chain,
    path="/retriever",
)

app.include_router(
    ingest.router,
    dependencies=[Depends(verify_auth_token)],
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/health")
async def health():
    return Response(status_code=status.HTTP_200_OK)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
