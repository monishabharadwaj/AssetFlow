from pydantic import BaseModel


class AssistantChatRequest(BaseModel):
    message: str


class AssistantSource(BaseModel):
    label: str
    asset_id: str
    url: str


class AssistantChatResponse(BaseModel):
    answer: str
    tools_used: list[str] = []
    sources: list[AssistantSource] = []
