from pydantic import BaseModel, Field


class InvestigateRequest(BaseModel):
    context: str | None = None


class ProgressEvent(BaseModel):
    step: str
    status: str
    type: str = "progress"
