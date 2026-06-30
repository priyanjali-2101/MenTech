from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from auth.auth_bearer import JWTBearer
from ai.risk_analyzer import analyze_risk_priority, generate_mitigation, generate_risk_summary
from ai.chatbot import chat_with_risks
from ai.workflow import run_risk_workflow
from ai import mcp_tools

router = APIRouter(prefix="/ai", tags=["AI Features"])


# ============ SCHEMAS ============
class AnalyzeRequest(BaseModel):
    title      : str
    description: str

class MitigationRequest(BaseModel):
    title      : str
    description: str
    priority   : str

class ChatRequest(BaseModel):
    question: str

class WorkflowRequest(BaseModel):
    risk_id    : int
    title      : str
    description: str

class CreateRiskRequest(BaseModel):
    title      : str
    description: str
    priority   : str
    category   : str
    due_date   : Optional[str] = None
    mitigation : Optional[str] = None

class UpdateRiskRequest(BaseModel):
    risk_id   : int
    status    : Optional[str] = None
    priority  : Optional[str] = None
    mitigation: Optional[str] = None

class AssignRiskRequest(BaseModel):
    risk_id    : int
    assigned_to: int

class SearchRequest(BaseModel):
    keyword : Optional[str] = None
    status  : Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None


# ============ AI APIS ============
@router.post("/analyze")
def analyze_risk(request: AnalyzeRequest, current_user: dict = Depends(JWTBearer())):
    return {"input": request.dict(), "analysis": analyze_risk_priority(request.title, request.description)}

@router.post("/mitigation")
def get_mitigation(request: MitigationRequest, current_user: dict = Depends(JWTBearer())):
    return {"mitigation_plan": generate_mitigation(request.title, request.description, request.priority)}

@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return {"question": request.question, "answer": chat_with_risks(request.question, db)}

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return {"summary": generate_risk_summary(mcp_tools.get_all_risks(db))}

@router.post("/workflow")
def run_workflow(request: WorkflowRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return run_risk_workflow(request.risk_id, request.title, request.description, db)


# ============ MCP APIS ============
@router.post("/mcp/create-risk")
def mcp_create(request: CreateRiskRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.create_risk(db, request.title, request.description,
                                  request.priority, request.category,
                                  current_user["user_id"], request.due_date, request.mitigation)

@router.post("/mcp/update-risk")
def mcp_update(request: UpdateRiskRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.update_risk(db, request.risk_id, request.status,
                                  request.priority, request.mitigation, current_user["user_id"])

@router.post("/mcp/assign-risk")
def mcp_assign(request: AssignRiskRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.assign_risk(db, request.risk_id, request.assigned_to, current_user["user_id"])

@router.post("/mcp/search")
def mcp_search(request: SearchRequest, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.search_risks(db, request.keyword, request.status, request.priority, request.category)

@router.delete("/mcp/delete-risk/{risk_id}")
def mcp_delete(risk_id: int, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.delete_risk(db, risk_id)

@router.get("/mcp/dashboard")
def mcp_dashboard(db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.get_dashboard(db)

@router.get("/mcp/users")
def mcp_users(db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.get_all_users(db)

@router.get("/mcp/comments/{risk_id}")
def mcp_comments(risk_id: int, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.get_comments(db, risk_id)

@router.get("/mcp/activity/{risk_id}")
def mcp_activity(risk_id: int, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer())):
    return mcp_tools.get_activity_logs(db, risk_id)