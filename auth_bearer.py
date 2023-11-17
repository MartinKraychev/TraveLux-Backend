from jose import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends


ALGORITHM = "HS256"
JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"


def decode_jwt(jw_token: str):
    try:
        # Decode and verify the token
        payload = jwt.decode(jw_token, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except jwt.JWTError:
        return None


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            payload = decode_jwt(credentials.credentials)
            request.state.current_user = payload
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")

            return credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


def get_token_credentials(credentials: HTTPAuthorizationCredentials = Depends(JWTBearer())) -> str:
    return credentials.credentials
