import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import config

security = HTTPBearer()


def verify_auth_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    if not secrets.compare_digest(credentials.credentials, config.AUTH_TOKEN):
        raise HTTPException(status_code=403, detail="Unauthorized")
