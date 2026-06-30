from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.db import get_db
from schemas.comment_schema import CommentCreate, CommentResponse
from services import comment_logic
from auth.auth_bearer import JWTBearer

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=CommentResponse)
def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return comment_logic.add_comment(db, comment, current_user)


@router.get("/{risk_id}", response_model=List[CommentResponse])
def get_comments(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return comment_logic.get_comments_by_risk(db, risk_id)