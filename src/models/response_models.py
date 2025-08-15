"""
Response models for MentorIA Chatbot API.

Pydantic models for API response validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Model for chat interaction responses."""
    
    conversation_id: str = Field(..., description="Current conversation ID")
    response_type: str = Field(..., description="Response type to render: 'text', 'buttons', or 'content_cards'")
    data: Dict[str, Any] = Field(..., description="Data payload corresponding to response_type")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContentResponse(BaseModel):
    """Model for content operation responses."""
    
    id: str = Field(..., description="Content unique identifier")
    title: str = Field(..., description="Content title")
    description: str = Field(..., description="Content description")
    content: str = Field(..., description="Main content text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ContentListResponse(BaseModel):
    """Model for content list responses."""
    
    items: List[ContentResponse] = Field(..., description="List of content items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")


class SuccessResponse(BaseModel):
    """Model for successful operation responses."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageResponse(BaseModel):
    """Model for individual message responses."""
    
    id: str = Field(..., description="Message unique identifier")
    user_id: str = Field(..., description="User ID who sent the message")
    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="Message content")
    message_type: str = Field(..., description="Type of message: 'user' or 'bot'")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")


class MessageListResponse(BaseModel):
    """Model for paginated message list responses."""
    
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class ConversationResponse(BaseModel):
    """Model for conversation information responses."""
    
    conversation_id: str = Field(..., description="Conversation unique identifier")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    last_message_at: Optional[datetime] = Field(None, description="Last message timestamp")
    message_count: int = Field(..., description="Total number of messages in conversation")
    is_active: bool = Field(..., description="Whether conversation is still active") 