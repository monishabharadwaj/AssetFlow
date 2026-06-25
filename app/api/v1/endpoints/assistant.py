from fastapi import APIRouter, Depends

from app.api.deps import get_assistant_service
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter()


@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(
    request: AssistantChatRequest,
    service: AssistantService = Depends(get_assistant_service),
) -> AssistantChatResponse:
    return await service.chat(request)
