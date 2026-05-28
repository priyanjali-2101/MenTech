from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from schemas.user_validation import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from services import user_logic
from auth.auth_bearer import JWTBearer
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    result = user_logic.create_user(db, user)
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered hai")
    return result


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    result = user_logic.login_user(db, user.email, user.password)
    if not result:
        raise HTTPException(status_code=401, detail="Email ya password galat hai")
    return result


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return user_logic.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    user = user_logic.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    updated = user_logic.update_user(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User nahi mila")
    return updated


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    result = user_logic.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User nahi mila")
    return result