from pydantic import BaseModel, Field


class RepositoryImportRequest(BaseModel):
    repo_url: str = Field(min_length=1)


class RepositoryActivationRequest(BaseModel):
    repository_path: str = Field(min_length=1)
