"""Pydantic request/response models — validated, typed API contracts."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

Status = Literal["Not Started", "Attempted", "Solved w/ Hint", "Solved Solo", "Needs Revision"]


class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    provider: str = "local"


class StatusIn(BaseModel):
    problem_id: str
    status: Status
    note: str = Field(default="", max_length=2000)


class RevisionIn(BaseModel):
    problem_id: str
    on: bool = True


class AssistantIn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    problem_id: Optional[str] = None


class AssistantOut(BaseModel):
    answer: str
    source: Literal["offline-tutor", "llm"]


TokenOut.model_rebuild()
