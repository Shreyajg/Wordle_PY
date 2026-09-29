import base64
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

TOKEN_VALIDITY = timedelta(hours=1)


class JwtService:

    def __init__(self, secret: str):
        self.key = base64.b64decode(secret)
        if len(self.key) < 32:
            raise ValueError("JWT_SECRET must decode to at least 256 bits (32 bytes)")
        if len(self.key) >= 64:
            self.algorithm = "HS512"
        elif len(self.key) >= 48:
            self.algorithm = "HS384"
        else:
            self.algorithm = "HS256"

    def generate_token(self, username: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {"sub": username, "iat": now, "exp": now + TOKEN_VALIDITY}
        return jwt.encode(payload, self.key, algorithm=self.algorithm)

    def extract_username(self, token: str) -> Optional[str]:
        """Returns None for an expired, tampered or malformed token."""
        try:
            claims = jwt.decode(token, self.key, algorithms=["HS256", "HS384", "HS512"])
        except jwt.PyJWTError:
            return None
        return claims.get("sub")

    def validate_token(self, token: str, username: str) -> bool:
        token_username = self.extract_username(token)
        return token_username is not None and token_username == username
