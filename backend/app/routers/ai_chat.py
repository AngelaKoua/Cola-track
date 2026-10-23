from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Literal
from app.services.ai.chat_service import generate_chat_response

router = APIRouter(prefix="/ai/chat", tags=["AI Chatbot"])

class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    content: str
    
class ChatContext(BaseModel):
    page: Optional[str] = None
    machine: Optional[str] = None
    indicators: Optional[str] = None
    
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: ChatContext
    
class ChatResponse(BaseModel):
    explanation: str
    interpretation: Optional[str] = None
    actions: List[str] = []

@router.post("/", response_model=ChatResponse)
async def chat_with_colaassist(request: ChatRequest):
    """
    Endpoint for ColaAssist chatbot.
    Receives conversation history and platform context, returns structured JSON.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    context_dict = {
        "page": request.context.page,
        "machine": request.context.machine,
        "indicators": request.context.indicators
    }
    
    result = await generate_chat_response(messages_dict, context_dict)
    
    return ChatResponse(
        explanation=result.get("Explication", "Je ne peux pas répondre pour le moment."),
        interpretation=result.get("Interprétation"),
        actions=result.get("Actions", [])
    )
