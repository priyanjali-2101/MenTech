from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from ai.mcp_tools import (
    get_all_risks,
    get_risks_by_priority,
    get_risks_by_status,
    get_dashboard
)

import json

llm = OllamaLLM(model="llama3.2")


def chat_with_risks(question: str, db: Session) -> str:

    # Database se data lo
    all_risks     = get_all_risks(db)
    dashboard     = get_dashboard(db)
    critical      = get_risks_by_priority(db, "Critical")
    open_risks    = get_risks_by_status(db, "Open")

    prompt = PromptTemplate(
        input_variables=["question", "dashboard", "risks", "critical", "open_risks"],
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
        
        User Question: {question}
        
        Answer the question based on the risk data above.
        Be concise and helpful.
        """
    )

    chain = prompt | llm

    result = chain.invoke({
        "question"   : question,
        "dashboard"  : json.dumps(dashboard, indent=2),
        "risks"      : json.dumps(all_risks, indent=2),
        "critical"   : json.dumps(critical, indent=2),
        "open_risks" : json.dumps(open_risks, indent=2)
    })

    return result.strip()