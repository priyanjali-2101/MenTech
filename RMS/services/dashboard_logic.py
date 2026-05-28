from sqlalchemy.orm import Session
from model.risk_table import Risk


def get_dashboard_summary(db: Session):
    return {
        "total_risks"    : db.query(Risk).count(),
        "open_risks"     : db.query(Risk).filter(Risk.status == "Open").count(),
        "in_progress"    : db.query(Risk).filter(Risk.status == "In Progress").count(),
        "resolved_risks" : db.query(Risk).filter(Risk.status == "Resolved").count(),
        "closed_risks"   : db.query(Risk).filter(Risk.status == "Closed").count(),
        "critical_risks" : db.query(Risk).filter(Risk.priority == "Critical").count(),
        "high_risks"     : db.query(Risk).filter(Risk.priority == "High").count(),
        "medium_risks"   : db.query(Risk).filter(Risk.priority == "Medium").count(),
        "low_risks"      : db.query(Risk).filter(Risk.priority == "Low").count(),
    }