from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama
from sqlalchemy.orm import Session

from ai.tools import get_tools

# Load LLM once
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

# LangChain's standard tool-calling prompt
prompt = hub.pull("hwchase17/openai-tools-agent")


def chat_with_risks(question: str, db: Session):

    tools = get_tools(db)

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=False,
    )

    result = executor.invoke(
        {
            "input": question
        }
    )

    return result["output"]