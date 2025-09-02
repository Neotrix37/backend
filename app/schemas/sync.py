from datetime import datetime
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')

class SyncResponse(GenericModel, Generic[T]):
    """Resposta genérica para endpoints de sincronização"""
    synced_records: List[T] = []
    conflicts: List[T] = []
    server_updated: List[T] = []

class SyncBase(BaseModel):
    """Campos base para todos os modelos sincronizáveis"""
    last_updated: datetime
    synced: bool = False

class SyncQuery(BaseModel):
    """Parâmetros para consulta de sincronização"""
    last_sync: datetime