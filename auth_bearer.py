from jose import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from sqlalchemy.orm import Session

from database_operations import token_operations
from db import get_db

ALGORITHM = "HS256"
JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"


def decode_jwt(jw_token: str):
    """
    Decodes a token if possible
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(jw_token, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except jwt.JWTError:
        return None


class JWTBearer(HTTPBearer):
    """
    Auth bearer to check JWT eligibility
    """
    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            payload = decode_jwt(credentials.credentials)
            request.state.current_user = payload
            if not payload:
                token_operations.set_inactive_token(db, credentials.credentials)
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            return credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


def get_token_credentials(credentials: HTTPAuthorizationCredentials = Depends(JWTBearer())) -> str:
    """
    Creates a token dependency
    """
    return credentials.credentials
