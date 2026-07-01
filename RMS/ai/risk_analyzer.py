from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Ollama model load karo
llm = OllamaLLM(model="llama3.2")

# Risk Priority Analyze karo
def analyze_risk_priority(title: str, description: str) -> dict:
    prompt = PromptTemplate(
        input_variables=["title", "description"],
        template="""
        You are a risk management expert. Analyze this risk and respond in JSON only.

        Risk Title: {title}
        Risk Description: {description}

        Respond ONLY in this JSON format, nothing else:
        {{
            "priority": "Critical or High or Medium or Low",
            "category": "Security or Infrastructure or Bug or Performance or Maintenance",
            "mitigation": "Short mitigation plan in one line",
            "reason": "Why this priority in one line"
        }}
        """
    )

    chain = prompt | llm

    result = chain.invoke({
        "title": title,
        "description": description
    })

    # JSON parse karo
    import json
    import re

    try:
        # JSON dhundo response mein
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass

    # Fallback
    return {
        "priority": "Medium",
        "category": "General",
        "mitigation": "Please review manually",
        "reason": "Could not analyze automatically"
    }


# Mitigation Plan Generate karo
def generate_mitigation(title: str, description: str, priority: str) -> str:
    prompt = PromptTemplate(
        input_variables=["title", "description", "priority"],
        template="""
        You are a risk management expert.
        
        Risk: {title}
        Description: {description}
        Priority: {priority}
        
        Give a detailed mitigation plan in 3-4 steps.
        Be specific and practical.
        """
    )

    chain = prompt | llm

    result = chain.invoke({
        "title": title,
        "description": description,
        "priority": priority
    })

    return result.strip()


# Risk Summary Generate karo
def generate_risk_summary(risks: list) -> str:
    if not risks:
        return "No risks found to summarize."

    risks_text = "\n".join([
        f"- {r['title']} | Priority: {r['priority']} | Status: {r['status']}"
        for r in risks
    ])

    prompt = PromptTemplate(
        input_variables=["risks"],
        template="""
        You are a risk management expert.

        Here are the current risks:
        {risks}

        Give a brief executive summary in 3-4 lines.
        Highlight the most critical issues.
        """
    )

    chain = prompt | llm
    result = chain.invoke({"risks": risks_text})
    return result.strip()


# Error hai kuch isme. areee waha streamlit pr start kar perfrom karna  