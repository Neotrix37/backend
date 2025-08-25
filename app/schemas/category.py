from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseResponse, BaseCreate, BaseUpdate

class CategoryCreate(BaseCreate):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")

class CategoryUpdate(BaseUpdate):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")

class CategoryResponse(BaseResponse):
    name: str
    description: Optional[str]
    color: Optional[str]
