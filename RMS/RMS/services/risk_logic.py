from sqlalchemy.orm import Session
from sqlalchemy import or_
from model.risk_table import Risk
from model.activity_table import Activity
from schemas.risk_validation import RiskCreate, RiskUpdate


def create_risk(db: Session, risk_data: RiskCreate, current_user: dict):
    new_risk = Risk(
        title       = risk_data.title,
        description = risk_data.description,
        priority    = risk_data.priority,
        status      = risk_data.status,
        category    = risk_data.category,
        assigned_to = risk_data.assigned_to,
        created_by  = current_user["user_id"],
        due_date    = risk_data.due_date,
        mitigation  = risk_data.mitigation
    )
    db.add(new_risk)
    db.commit()
    db.refresh(new_risk)

    # Activity log
    log = Activity(
        action  = f"Risk '{new_risk.title}' create kiya gaya",
        risk_id = new_risk.id,
        done_by = current_user["user_id"]
    )
    db.add(log)
    db.commit()

    return new_risk


def get_all_risks(db: Session, status: str = None, priority: str = None,
                  search: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Risk)

    # Filters
    if status:
        query = query.filter(Risk.status == status)
    if priority:
        query = query.filter(Risk.priority == priority)
    if search:
        query = query.filter(Risk.title.contains(search))

    # Pagination
    return query.offset(skip).limit(limit).all()


def get_risk_by_id(db: Session, risk_id: int):
    return db.query(Risk).filter(Risk.id == risk_id).first()


def update_risk(db: Session, risk_id: int, risk_data: RiskUpdate, current_user: dict):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        return None

    if risk_data.title is not None:
        risk.title = risk_data.title
    if risk_data.description is not None:
        risk.description = risk_data.description
    if risk_data.priority is not None:
        risk.priority = risk_data.priority
    if risk_data.status is not None:
        risk.status = risk_data.status
    if risk_data.category is not None:
        risk.category = risk_data.category
    if risk_data.assigned_to is not None:
        risk.assigned_to = risk_data.assigned_to
    if risk_data.due_date is not None:
        risk.due_date = risk_data.due_date
    if risk_data.mitigation is not None:
        risk.mitigation = risk_data.mitigation

    db.commit()
    db.refresh(risk)

    # Activity log
    log = Activity(
        action  = f"Risk '{risk.title}' update kiya gaya",
        risk_id = risk.id,
        done_by = current_user["user_id"]
    )
    db.add(log)
    db.commit()

    return risk


def delete_risk(db: Session, risk_id: int):
    risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not risk:
        return None
    db.delete(risk)
    db.commit()
    return {"message": f"Risk {risk_id} deleted successfully"}


def get_dashboard(db: Session):
    total    = db.query(Risk).count()
    open     = db.query(Risk).filter(Risk.status == "Open").count()
    progress = db.query(Risk).filter(Risk.status == "In Progress").count()
    resolved = db.query(Risk).filter(Risk.status == "Resolved").count()
    closed   = db.query(Risk).filter(Risk.status == "Closed").count()
    critical = db.query(Risk).filter(Risk.priority == "Critical").count()

    return {
        "total_risks"    : total,
        "open_risks"     : open,
        "in_progress"    : progress,
        "resolved_risks" : resolved,
        "closed_risks"   : closed,
        "critical_risks" : critical
    }