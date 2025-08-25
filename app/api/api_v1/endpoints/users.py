from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Any

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.api_v1.endpoints.auth import get_password_hash


router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)) -> Any:
    users = db.query(User).filter(User.is_active == True).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Username único
    existing_username = db.query(User).filter(User.username == user_data.username, User.is_active == True).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com este username")

    # Email (se fornecido) único
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email, User.is_active == True).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com este email")

    user_dict = user_data.model_dump()
    # mapear is_admin (do desktop) para role/is_superuser
    is_admin_flag = bool(user_dict.pop("is_admin", False))
    salary = user_dict.pop("salary", None)

    # senha
    plain_password = user_dict.pop("password")
    user_dict["hashed_password"] = get_password_hash(plain_password)

    # papel
    if is_admin_flag:
        user_dict["role"] = UserRole.ADMIN
        user_dict["is_superuser"] = True

    if salary is not None:
        user_dict["salary"] = salary

    new_user = User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    update_dict = user_data.model_dump(exclude_unset=True)

    # Validar unicidade username/email
    if "username" in update_dict and update_dict["username"] != user.username:
        existing_username = db.query(User).filter(User.username == update_dict["username"], User.is_active == True, User.id != user_id).first()
        if existing_username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com este username")
    if "email" in update_dict and update_dict["email"]:
        existing_email = db.query(User).filter(User.email == update_dict["email"], User.is_active == True, User.id != user_id).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com este email")

    # Atualização opcional de senha
    if "password" in update_dict and update_dict["password"]:
        user.hashed_password = get_password_hash(update_dict.pop("password"))
    elif "password" in update_dict:
        # não atualizar quando vazio
        update_dict.pop("password")

    # Mapear is_admin opcional
    if "is_admin" in update_dict:
        is_admin_flag = bool(update_dict.pop("is_admin"))
        if is_admin_flag:
            user.role = UserRole.ADMIN
            user.is_superuser = True
        else:
            # Se desmarcar admin, manter role atual se não informado explicitamente
            if not update_dict.get("role"):
                user.role = user.role or UserRole.VIEWER
            user.is_superuser = False

    # Aplicar demais campos simples
    for field, value in update_dict.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    user.is_active = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


