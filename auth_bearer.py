from jose import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


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
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(jw_token: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jw_token)
        except jwt.JWTError:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid


jwt_bearer = JWTBearer()
