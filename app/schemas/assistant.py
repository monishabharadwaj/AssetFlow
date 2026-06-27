from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class AssistantSource(BaseModel):
    label: str
    asset_id: str
    url: str


class AssistantChatResponse(BaseModel):
    answer: str
    tools_used: list[str] = []
    sources: list[AssistantSource] = []
