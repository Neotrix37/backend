from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .sync import SyncBase

class BaseSchema(BaseModel):
    """Schema base com configurações comuns"""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )

class BaseResponse(BaseSchema):
    """Schema base para respostas"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

class BaseCreate(BaseSchema, SyncBase):
    """Schema base para criação"""
    pass

class BaseUpdate(BaseSchema):
    """Schema base para atualização"""
    pass
