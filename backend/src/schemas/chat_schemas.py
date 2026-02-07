"""Pydantic schemas for chat endpoints."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint.

    Attributes:
        message: User's natural language message
        conversation_id: Optional conversation ID to continue existing conversation
        confirm_action: Optional confirmation response for destructive operations
    """
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID to continue")
    confirm_action: Optional[dict] = Field(None, description="Confirmation response with action and params")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint.

    Attributes:
        message: Assistant's response message
        conversation_id: Conversation ID (new or existing)
        requires_confirmation: Whether user confirmation is required
        confirmation_details: Details about required confirmation (if any)
    """
    message: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID")
    requires_confirmation: bool = Field(default=False, description="Whether confirmation is required")
    confirmation_details: Optional[dict] = Field(None, description="Confirmation details")


class ConversationResponse(BaseModel):
    """Response schema for conversation metadata.

    Attributes:
        id: Conversation UUID
        title: Conversation title
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = Field(..., description="Conversation UUID")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MessageResponse(BaseModel):
    """Response schema for individual messages.

    Attributes:
        id: Message UUID
        role: Message role (user, assistant, system)
        content: Message content
        created_at: Creation timestamp
    """
    id: str = Field(..., description="Message UUID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Creation timestamp")
