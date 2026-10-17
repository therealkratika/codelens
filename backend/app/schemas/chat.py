from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str | None = Field(default=None, min_length=1)


class ChatSessionCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class ChatSessionRenameRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
