#!/usr/bin/env python
from fastapi import Depends
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from langserve import add_routes

from app.chains.chat import chat_chain
from app.dependencies.auth_token import verify_auth_token
from app.routers import ingest

app = FastAPI(
    title="Chat Search",
    version="1.0",
    description="Chat Search for documents",
)

add_routes(
    app,
    chat_chain,
    path="/chat",
)

app.include_router(
    ingest.router,
    dependencies=[Depends(verify_auth_token)],
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
