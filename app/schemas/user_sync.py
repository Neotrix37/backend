from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from .user import UserRole

class UserSyncResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    full_name: str
    role: UserRole
    is_superuser: bool
    is_active: bool
    salary: Optional[Decimal]
    last_updated: datetime
    synced: bool

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
        }