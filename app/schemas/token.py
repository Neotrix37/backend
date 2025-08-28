from pydantic import BaseModel
from typing import Optional, Dict, Any

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    user: Optional[Dict[str, Any]] = None

class TokenData(BaseModel):
    username: str | None = None
