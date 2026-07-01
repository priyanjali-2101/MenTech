from sqlalchemy.orm import Session
from database.db import SessionLocal
from model.risk_table import Risk
from model.user_table import User
from model.comment_table import Comment
from model.activity_table import Activity

#  RISK TOOLS 

def get_all_risks(db: Session) -> list:
    risks = db.query(Risk).all()
    return [{"id": r.id, "title": r.title, "priority": r.priority,
             "status": r.status, "category": r.category,
             "assigned_to": r.assigned_to, "due_date": r.due_date} for r in risks]


def get_risks_by_priority(db: Session, priority: str) -> list:
    risks = db.query(Risk).filter(Risk.priority == priority).all()
    return [{"id": r.id, "title": r.title, "priority": r.priority,
             "status": r.status, "due_date": r.due_date} for r in risks]


def get_risks_by_status(db: Session, status: str) -> list:
    risks = db.query(Risk).filter(Risk.status == status).all()
    return [{"id": r.id, "title": r.title, "priority": r.priority,
             "status": r.status, "due_date": r.due_date} for r in risks]


def create_risk(db: Session, title: str, description: str, priority: str,
                category: str, created_by: int, due_date: str = None,
                mitigation: str = None) -> dict:
    risk = Risk(title=title, description=description, priority=priority,
                status="Open", category=category, created_by=created_by,
                due_date=due_date, mitigation=mitigation)
    db.add(risk)
    db.commit()
    db.refresh(risk)
    db.add(Activity(action=f"Risk '{title}' created", risk_id=risk.id, done_by=created_by))
    db.commit()
    return {"message": "Risk created!", "risk_id": risk.id, "title": risk.title,
            "priority": risk.priority, "status": risk.status}


def update_risk(db: Session, risk_id: int, status: str = None,
                priority: str = None, mitigation: str = None,
                done_by: int = None) -> dict:
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        return {"error": f"Risk {risk_id} not found"}
    old = risk.status
    if status:    risk.status = status
    if priority:  risk.priority = priority
    if mitigation: risk.mitigation = mitigation
    db.commit()
    db.refresh(risk)
    if done_by:
        db.add(Activity(action=f"Risk updated: {old}→{risk.status}",
                        risk_id=risk.id, done_by=done_by))
        db.commit()
    return {"message": "Risk updated!", "risk_id": risk.id,
            "status": risk.status, "priority": risk.priority}


def assign_risk(db: Session, risk_id: int, assigned_to: int,
                done_by: int = None) -> dict:
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    user = db.query(User).filter(User.id == assigned_to).first()
    if not risk: return {"error": f"Risk {risk_id} not found"}
    if not user: return {"error": f"User {assigned_to} not found"}
    risk.assigned_to = assigned_to
    risk.status = "Assigned"
    db.commit()
    if done_by:
        db.add(Activity(action=f"Risk assigned to {user.name}",
                        risk_id=risk.id, done_by=done_by))
        db.commit()
    return {"message": "Risk assigned!", "risk_id": risk.id,
            "assigned_to": user.name, "status": risk.status}


def delete_risk(db: Session, risk_id: int) -> dict:
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk: return {"error": f"Risk {risk_id} not found"}
    title = risk.title

    # Pehle linked activities aur comments delete karo
    # (warna FK constraint error aata hai: NOT NULL constraint failed)
    db.query(Activity).filter(Activity.risk_id == risk_id).delete()
    db.query(Comment).filter(Comment.risk_id == risk_id).delete()

    db.delete(risk)
    db.commit()
    return {"message": f"Risk '{title}' deleted!", "risk_id": risk_id}


def search_risks(db: Session, keyword: str = None, status: str = None,
                 priority: str = None, category: str = None) -> list:
    q = db.query(Risk)
    if keyword:  q = q.filter(Risk.title.contains(keyword) | Risk.description.contains(keyword))
    if status:   q = q.filter(Risk.status == status)
    if priority: q = q.filter(Risk.priority == priority)
    if category: q = q.filter(Risk.category == category)
    risks = q.all()
    if not risks: return [{"message": "No risks found"}]
    return [{"id": r.id, "title": r.title, "priority": r.priority,
             "status": r.status, "category": r.category} for r in risks]


# USER TOOLS 

def get_all_users(db: Session) -> list:
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email,
             "role": u.role} for u in users]


def get_user_by_id(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user: return {"error": "User not found"}
    return {"id": user.id, "name": user.name,
            "email": user.email, "role": user.role}


# DASHBOARD TOOL

def get_dashboard(db: Session) -> dict:
    return {
        "total_risks"   : db.query(Risk).count(),
        "open_risks"    : db.query(Risk).filter(Risk.status == "Open").count(),
        "in_progress"   : db.query(Risk).filter(Risk.status == "In Progress").count(),
        "resolved_risks": db.query(Risk).filter(Risk.status == "Resolved").count(),
        "closed_risks"  : db.query(Risk).filter(Risk.status == "Closed").count(),
        "critical_risks": db.query(Risk).filter(Risk.priority == "Critical").count(),
        "high_risks"    : db.query(Risk).filter(Risk.priority == "High").count(),
    }


# COMMENT TOOLS 

def get_comments(db: Session, risk_id: int) -> list:
    comments = db.query(Comment).filter(Comment.risk_id == risk_id).all()
    return [{"id": c.id, "content": c.content,
             "user_id": c.user_id} for c in comments]


def add_comment(db: Session, risk_id: int,
                content: str, user_id: int) -> dict:
    comment = Comment(content=content, risk_id=risk_id, user_id=user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"message": "Comment added!", "comment_id": comment.id}


#  ACTIVITY TOOL 

def get_activity_logs(db: Session, risk_id: int) -> list:
    logs = db.query(Activity).filter(Activity.risk_id == risk_id).all()
    return [{"id": l.id, "action": l.action,
             "done_by": l.done_by} for l in logs]