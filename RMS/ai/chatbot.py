from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from ai.mcp_tools import (
    get_all_risks,
    get_risks_by_priority,
    get_risks_by_status,
    get_dashboard,
    create_risk,
    update_risk,
    assign_risk,
    delete_risk,
)

import json
import re

llm = OllamaLLM(model="llama3.2")


# ── Helper: find a risk_id by fuzzy title match ─────────────────────────────
# Lets the user say "delete the printer risk" instead of needing to know the
# numeric ID. Picks the risk whose title shares the most words with the hint.
def find_risk_id_by_title(hint: str, db: Session):
    if not hint:
        return None
    hint_words = set(re.findall(r'\w+', hint.lower()))
    if not hint_words:
        return None

    risks = get_all_risks(db)
    best_id, best_score = None, 0
    for r in risks:
        title_words = set(re.findall(r'\w+', r["title"].lower()))
        score = len(hint_words & title_words)
        if score > best_score:
            best_score, best_id = score, r["id"]

    return best_id if best_score > 0 else None


# ── Step 1: Ask the model whether this question is a WRITE request ──────────
# Kept as a separate, narrow prompt so the small local model only has to make
# one decision at a time (intent + action), instead of mixing free-form chat
# with structured tool output in a single call. Much more reliable this way.
def detect_action(question: str) -> dict:
    prompt = PromptTemplate(
        input_variables=["question"],
        template="""
        You are an intent classifier for a Risk Management system.

        Decide if the user's message is asking to CREATE, UPDATE, ASSIGN,
        or DELETE a risk, or if it is just a normal QUESTION (read-only).

        User message: {question}

        Respond ONLY with JSON in exactly one of these formats, nothing else:

        For creating a risk:
        {{"action": "create", "title": "...", "description": "...", "priority": "Critical|High|Medium|Low", "category": "Security|Infrastructure|Bug|Performance|Maintenance"}}

        For updating a risk's status/priority/mitigation:
        {{"action": "update", "risk_id": 0, "risk_hint": "any name/words the user used to refer to the risk, or empty string", "status": "Open|Assigned|In Progress|Resolved|Closed or null", "priority": "Critical|High|Medium|Low or null", "mitigation": "... or null"}}

        For assigning a risk to a user:
        {{"action": "assign", "risk_id": 0, "risk_hint": "any name/words the user used to refer to the risk, or empty string", "assigned_to": 0}}

        For deleting a risk:
        {{"action": "delete", "risk_id": 0, "risk_hint": "any name/words the user used to refer to the risk, or empty string"}}

        Rules:
        - If the user gives a numeric risk ID, put it in "risk_id" and leave "risk_hint" empty.
        - If the user only describes the risk by name/words (e.g. "the printer risk", "Random Risk 1"), set "risk_id" to 0 and put those describing words in "risk_hint".
        - For anything else (questions, summaries, status checks), respond with {{"action": "none"}}.

        For anything else:
        {{"action": "none"}}
        """
    )

    chain = prompt | llm
    result = chain.invoke({"question": question})

    print("=" * 50)
    print("RAW LLM RESPONSE FOR ACTION DETECTION:")
    print(result)
    print("=" * 50)

    try:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {"action": "none"}


# ── Step 2: Execute the requested write operation safely ───────────────────
def execute_action(action: dict, db: Session, user_id: int) -> str:
    kind = action.get("action")

    print("=" * 50)
    print("DETECTED ACTION:", action)
    print("=" * 50)

    # Resolve risk_id from a name hint if no numeric id was given
    risk_id = action.get("risk_id") or 0
    if kind in ("update", "assign", "delete") and not risk_id:
        hint = action.get("risk_hint", "")
        resolved = find_risk_id_by_title(hint, db)
        print("RESOLVED RISK ID FROM HINT:", hint, "->", resolved)
        if resolved is None:
            return f"⚠️ Couldn't find a risk matching \"{hint}\". Please mention the risk ID or a more specific title."
        risk_id = resolved

    try:
        if kind == "create":
            result = create_risk(
                db,
                title=action.get("title", "Untitled risk"),
                description=action.get("description", ""),
                priority=action.get("priority", "Medium"),
                category=action.get("category", "General"),
                created_by=user_id,
            )
            return f"✅ Created risk #{result['risk_id']} — \"{result['title']}\" (Priority: {result['priority']})"

        if kind == "update":
            result = update_risk(
                db,
                risk_id=risk_id,
                status=action.get("status"),
                priority=action.get("priority"),
                mitigation=action.get("mitigation"),
                done_by=user_id,
            )
            if "error" in result:
                return f"⚠️ {result['error']}"
            return f"✅ Updated risk #{result['risk_id']} — Status: {result['status']}, Priority: {result['priority']}"

        if kind == "assign":
            result = assign_risk(
                db,
                risk_id=risk_id,
                assigned_to=action.get("assigned_to"),
                done_by=user_id,
            )
            if "error" in result:
                return f"⚠️ {result['error']}"
            return f"✅ Assigned risk #{result['risk_id']} to {result['assigned_to']}"

        if kind == "delete":
            result = delete_risk(db, risk_id=risk_id)
            if "error" in result:
                return f"⚠️ {result['error']}"
            return f"🗑️ {result['message']}"

    except Exception as e:
        print("=" * 50)
        print("EXECUTE ACTION ERROR:", str(e))
        print("=" * 50)
        return f"⚠️ Could not complete that action: {e}"

    return ""


def chat_with_risks(question: str, db: Session, user_id: int = None) -> str:

    # Database se data lo (always needed, even for write requests, so the
    # follow-up answer can reference up-to-date numbers)
    all_risks     = get_all_risks(db)
    dashboard     = get_dashboard(db)
    critical      = get_risks_by_priority(db, "Critical")
    open_risks    = get_risks_by_status(db, "Open")

    action_result = ""

    # Only attempt write actions if we know who is asking (auth required)
    if user_id is not None:
        action = detect_action(question)
        if action.get("action") != "none":
            action_result = execute_action(action, db, user_id)
            # Refresh data after a write so the model's answer reflects it
            all_risks  = get_all_risks(db)
            dashboard  = get_dashboard(db)
            critical   = get_risks_by_priority(db, "Critical")
            open_risks = get_risks_by_status(db, "Open")

    prompt = PromptTemplate(
        input_variables=["question", "dashboard", "risks", "critical", "open_risks", "action_result"],
        template="""
        You are a Risk Management AI Assistant.

        Current Dashboard:
        {dashboard}

        All Risks:
        {risks}

        Critical Risks:
        {critical}

        Open Risks:
        {open_risks}

        Action just performed (if any): {action_result}

        User Question: {question}

        If an action was just performed, confirm it briefly to the user in plain language.
        Otherwise answer the question based on the risk data above.
        Be concise and helpful.
        """
    )

    chain = prompt | llm

    result = chain.invoke({
        "question"     : question,
        "dashboard"    : json.dumps(dashboard, indent=2),
        "risks"        : json.dumps(all_risks, indent=2),
        "critical"     : json.dumps(critical, indent=2),
        "open_risks"   : json.dumps(open_risks, indent=2),
        "action_result": action_result if action_result else "None"
    })

    final = result.strip()
    if action_result:
        # Always surface the concrete result, even if the model's phrasing is vague
        final = f"{action_result}\n\n{final}"

    return final