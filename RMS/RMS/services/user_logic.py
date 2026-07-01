from sqlalchemy.orm import Session
from model.user_table import User
from schemas.user_validation import UserCreate, UserUpdate
from auth.auth_handler import hash_password, verify_password, create_token


def create_user(db: Session, user_data: UserCreate):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        return None

    new_user = User(
        name     = user_data.name,
        email    = user_data.email,
        password = hash_password(user_data.password),
        role     = user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None

    token = create_token(user.id, user.email, user.role)
    return {
        "access_token" : token,
        "token_type"   : "bearer",
        "user_id"      : user.id,
        "name"         : user.name,
        "role"         : user.role
    }


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if user_data.name is not None:
        user.name = user_data.name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}