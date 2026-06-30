from sqlalchemy.orm import Session
from model.comment_table import Comment
from schemas.comment_schema import CommentCreate


def add_comment(db: Session, comment_data: CommentCreate, current_user: dict):
    comment = Comment(
        content = comment_data.content,
        risk_id = comment_data.risk_id,
        user_id = current_user["user_id"]
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_risk(db: Session, risk_id: int):
    return db.query(Comment).filter(Comment.risk_id == risk_id).all()