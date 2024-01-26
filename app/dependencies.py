import os
import secrets
from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN is not set in the environment variables")


async def verify_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    if not secrets.compare_digest(credentials.credentials, AUTH_TOKEN):
        raise HTTPException(status_code=403, detail="Unauthorized")
