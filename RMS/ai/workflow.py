from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from typing import TypedDict, Optional
from sqlalchemy.orm import Session
from model.risk_table import Risk
from model.user_table import User
from ai.risk_analyzer import analyze_risk_priority

llm = OllamaLLM(model="llama3.2")


# State — Data is stored of the Workflow
class RiskState(TypedDict):
    risk_id      : int
    title        : str
    description  : str
    priority     : Optional[str]
    category     : Optional[str]
    mitigation   : Optional[str]
    assigned_to  : Optional[int]
    assigned_name: Optional[str]
    status       : Optional[str]
    message      : Optional[str]


# Node 1 — Analyze Risk 
def analyze_node(state: RiskState) -> RiskState:
    print(" Step 1: Analyzing risk...")

    result = analyze_risk_priority(
        state["title"],
        state["description"]
    )

    state["priority"]   = result.get("priority", "Medium")
    state["category"]   = result.get("category", "General")
    state["mitigation"] = result.get("mitigation", "Review manually")

    print(f"Priority: {state['priority']}")
    print(f"Category: {state['category']}")

    return state


# Node 2 — Find Best Employee 
def find_employee_node(state: RiskState, db: Session) -> RiskState:
    print(" Step 2: Finding best employee...")

    # Find Employees
    employees = db.query(User).filter(
        User.role == "Employee",
        User.is_active == "true"
    ).all()

    if not employees:
        state["assigned_to"]   = None
        state["assigned_name"] = "Unassigned"
        state["message"]       = "No active employees found"
        return state

    employee_workload = []
    for emp in employees:
        active_risks = db.query(Risk).filter(
            Risk.assigned_to == emp.id,
            Risk.status.in_(["Assigned", "In Progress"])
        ).count()

        employee_workload.append({
            "id"       : emp.id,
            "name"     : emp.name,
            "workload" : active_risks
        })

    best_employee = min(employee_workload, key=lambda x: x["workload"])

    state["assigned_to"]   = best_employee["id"]
    state["assigned_name"] = best_employee["name"]

    print(f"Assigned to: {best_employee['name']}")

    return state


# Node 3 — Update Risk in DataBase
def update_risk_node(state: RiskState, db: Session) -> RiskState:
    print("Step 3: Updating risk in database...")

    risk = db.query(Risk).filter(Risk.id == state["risk_id"]).first()

    if not risk:
        state["message"] = f"Risk {state['risk_id']} not found"
        return state

    risk.priority    = state["priority"]
    risk.category    = state["category"]
    risk.mitigation  = state["mitigation"]
    risk.assigned_to = state["assigned_to"]
    risk.status      = "Assigned" if state["assigned_to"] else "Open"

    db.commit()
    db.refresh(risk)

    state["status"]  = risk.status
    state["message"] = "Risk successfully analyzed and assigned!"

    print(f"Risk updated successfully!")

    return state


# Main Workflow Function
def run_risk_workflow(risk_id: int, title: str, description: str, db: Session) -> dict:

    print(f"\n Starting workflow for Risk #{risk_id}")
    print(f" Title: {title}")
    print("-" * 40)

    # Initial state
    state: RiskState = {
        "risk_id"      : risk_id,
        "title"        : title,
        "description"  : description,
        "priority"     : None,
        "category"     : None,
        "mitigation"   : None,
        "assigned_to"  : None,
        "assigned_name": None,
        "status"       : None,
        "message"      : None
    }

    # Step 1: Analyze
    state = analyze_node(state)

    # Step 2: Find Employee
    state = find_employee_node(state, db)

    # Step 3: Update Database
    state = update_risk_node(state, db)

    print("-" * 40)
    print(f"Workflow Complete!")

    return {
        "risk_id"      : state["risk_id"],
        "title"        : state["title"],
        "priority"     : state["priority"],
        "category"     : state["category"],
        "mitigation"   : state["mitigation"],
        "assigned_to"  : state["assigned_name"],
        "status"       : state["status"],
        "message"      : state["message"]
    }