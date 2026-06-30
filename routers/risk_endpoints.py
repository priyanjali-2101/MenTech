from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from schemas.risk_validation import RiskCreate, RiskUpdate, RiskResponse
from services import risk_logic
from auth.auth_bearer import JWTBearer
from auth.role_checker import check_role

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
def create_risk(
    risk: RiskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return risk_logic.create_risk(db, risk, current_user)


@router.get("/", response_model=List[RiskResponse])
def get_all_risks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return risk_logic.get_all_risks(db, status, priority, search, skip, limit)


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    return risk_logic.get_dashboard(db)


@router.get("/{risk_id}", response_model=RiskResponse)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    risk = risk_logic.get_risk_by_id(db, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.put("/{risk_id}", response_model=RiskResponse)
def update_risk(
    risk_id: int,
    risk: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    updated = risk_logic.update_risk(db, risk_id, risk, current_user)
    if not updated:
        raise HTTPException(status_code=404, detail="Risk not found")
    return updated


@router.delete("/{risk_id}")
def delete_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer())
):
    check_role(current_user, ["Admin"])
    result = risk_logic.delete_risk(db, risk_id)
    if not result:
        raise HTTPException(status_code=404, detail="Risk not found")
    return result
