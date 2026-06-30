from functools import partial
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai.mcp_tools import (
    get_all_risks,
    get_risks_by_priority,
    get_risks_by_status,
    create_risk,
    update_risk,
    assign_risk,
    delete_risk,
    search_risks,
    get_all_users,
    get_user_by_id,
    get_dashboard,
    get_comments,
    add_comment,
    get_activity_logs,
)


# ==========================
# Pydantic Schemas
# ==========================

class EmptyInput(BaseModel):
    """No input required."""


class PriorityInput(BaseModel):
    priority: str = Field(description="Risk priority (Critical, High, Medium, Low)")


class StatusInput(BaseModel):
    status: str = Field(description="Risk status (Open, Assigned, In Progress, Resolved, Closed)")


class DeleteRiskInput(BaseModel):
    risk_id: int


class UserInput(BaseModel):
    user_id: int


class RiskInput(BaseModel):
    risk_id: int


class SearchRiskInput(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None


class CreateRiskInput(BaseModel):
    title: str
    description: str
    priority: str
    category: str
    created_by: int
    due_date: Optional[str] = None
    mitigation: Optional[str] = None


class UpdateRiskInput(BaseModel):
    risk_id: int
    status: Optional[str] = None
    priority: Optional[str] = None
    mitigation: Optional[str] = None
    done_by: Optional[int] = None


class AssignRiskInput(BaseModel):
    risk_id: int
    assigned_to: int
    done_by: Optional[int] = None


class AddCommentInput(BaseModel):
    risk_id: int
    content: str
    user_id: int


# ==========================
# Tool Factory
# ==========================

def get_tools(db: Session):
    """
    Returns all LangChain tools with the current DB session bound.
    """

    return [

        StructuredTool.from_function(
            func=partial(get_all_risks, db),
            name="get_all_risks",
            description="Return all risks.",
            args_schema=EmptyInput,
        ),

        StructuredTool.from_function(
            func=partial(get_dashboard, db),
            name="get_dashboard",
            description="Return dashboard statistics.",
            args_schema=EmptyInput,
        ),

        StructuredTool.from_function(
            func=partial(get_risks_by_priority, db),
            name="get_risks_by_priority",
            description="Get risks by priority.",
            args_schema=PriorityInput,
        ),

        StructuredTool.from_function(
            func=partial(get_risks_by_status, db),
            name="get_risks_by_status",
            description="Get risks by status.",
            args_schema=StatusInput,
        ),

        StructuredTool.from_function(
            func=partial(search_risks, db),
            name="search_risks",
            description="Search risks using keyword, status, priority or category.",
            args_schema=SearchRiskInput,
        ),

        StructuredTool.from_function(
            func=partial(create_risk, db),
            name="create_risk",
            description="Create a new risk.",
            args_schema=CreateRiskInput,
        ),

        StructuredTool.from_function(
            func=partial(update_risk, db),
            name="update_risk",
            description="Update an existing risk.",
            args_schema=UpdateRiskInput,
        ),

        StructuredTool.from_function(
            func=partial(assign_risk, db),
            name="assign_risk",
            description="Assign a risk to a user.",
            args_schema=AssignRiskInput,
        ),

        StructuredTool.from_function(
            func=partial(delete_risk, db),
            name="delete_risk",
            description="Delete a risk by ID.",
            args_schema=DeleteRiskInput,
        ),

        StructuredTool.from_function(
            func=partial(get_all_users, db),
            name="get_all_users",
            description="Return all users.",
            args_schema=EmptyInput,
        ),

        StructuredTool.from_function(
            func=partial(get_user_by_id, db),
            name="get_user_by_id",
            description="Get user details by user ID.",
            args_schema=UserInput,
        ),

        StructuredTool.from_function(
            func=partial(get_comments, db),
            name="get_comments",
            description="Return comments for a risk.",
            args_schema=RiskInput,
        ),

        StructuredTool.from_function(
            func=partial(add_comment, db),
            name="add_comment",
            description="Add a comment to a risk.",
            args_schema=AddCommentInput,
        ),

        StructuredTool.from_function(
            func=partial(get_activity_logs, db),
            name="get_activity_logs",
            description="Return activity logs for a risk.",
            args_schema=RiskInput,
        ),
    ]