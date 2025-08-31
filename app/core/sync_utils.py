from typing import List, Type, TypeVar, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

ModelType = TypeVar('ModelType')

class SyncResult:
    """Classe para armazenar o resultado de uma operação de sincronização"""
    def __init__(self):
        self.synced_records: List[Dict[str, Any]] = []
        self.conflicts: List[Dict[str, Any]] = []
        self.server_updated: List[Dict[str, Any]] = []

def sync_models(
    db: Session,
    model: Type[ModelType],
    client_data: List[Dict[str, Any]],
    last_sync: datetime = None
) -> SyncResult:
    """
    Sincroniza dados do cliente com o servidor
    
    Args:
        db: Sessão do banco de dados
        model: Classe do modelo SQLAlchemy
        client_data: Lista de dicionários com dados do cliente
        last_sync: Data da última sincronização para buscar atualizações do servidor
    
    Returns:
        SyncResult: Resultado da sincronização
    """
    result = SyncResult()
    
    # Atualiza ou cria registros do cliente
    for item in client_data:
        try:
            db_item = db.query(model).get(item['id'])
            
            if db_item is None:
                # Cria novo registro
                db_item = model(**item)
                db.add(db_item)
                result.synced_records.append(item)
            else:
                # Atualiza registro existente se a versão do cliente for mais recente
                client_updated = item.get('last_updated')
                if client_updated and (db_item.last_updated is None or 
                                     client_updated > db_item.last_updated):
                    for key, value in item.items():
                        if hasattr(db_item, key) and key != 'id':
                            setattr(db_item, key, value)
                    result.synced_records.append(item)
                else:
                    result.conflicts.append(item)
            
            db_item.synced = True
            db_item.last_updated = datetime.utcnow()
            
        except Exception as e:
            # Em caso de erro, adiciona aos conflitos
            item['_error'] = str(e)
            result.conflicts.append(item)
    
    # Busca atualizações do servidor desde a última sincronização
    if last_sync:
        updated_items = db.query(model).filter(
            model.last_updated > last_sync,
            model.is_active == True
        ).all()
        
        for item in updated_items:
            result.server_updated.append(item.to_dict())
    
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
    return result
