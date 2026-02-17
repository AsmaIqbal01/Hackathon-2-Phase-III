"""Chat API endpoints for conversational AI interface."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from uuid import UUID
from src.auth.authenticator import get_current_user
from src.database import get_db
from src.models.user import User
from src.agents.master_agent import MasterAgent
from src.services.conversation_service import ConversationService
from src.schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse
)
from src.utils.errors import ConversationNotFoundError, UnauthorizedAccessError


# Create chat router
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a chat message through the AI agent.

    Stateless chat endpoint that:
    1. Validates JWT and extracts user_id
    2. Handles confirmation responses (if present)
    3. Instantiates MasterAgent with user context
    4. Processes message through agent chain
    5. Persists messages to database
    6. Returns response with confirmation status

    Args:
        request: Chat request with message and optional conversation_id
        user: Authenticated user from JWT (injected by get_current_user)
        db: Database session (injected by get_db)

    Returns:
        ChatResponse: Assistant's response with conversation context

    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors
    """
    try:
        # Extract user_id from User object
        user_id = user.id

        # Initialize ConversationService
        conv_service = ConversationService(db, user_id)

        # Handle confirmation responses
        if request.confirm_action:
            if not request.conversation_id:
                raise HTTPException(
                    status_code=400,
                    detail="conversation_id required for confirmation responses"
                )

            # Instantiate MasterAgent with conversation context
            agent = MasterAgent(user_id, UUID(request.conversation_id))
            await agent.connect_mcp()

            # Execute confirmed action
            result = await agent.confirmation_agent.execute_confirmed(
                request.confirm_action["action"],
                request.confirm_action["params"]
            )

            # Get result message
            result_message = result.get("message", "Action completed successfully.")

            # Save assistant response
            conv_service.add_message(
                UUID(request.conversation_id),
                "assistant",
                result_message
            )

            return ChatResponse(
                message=result_message,
                conversation_id=request.conversation_id,
                requires_confirmation=False
            )

        # Normal message processing
        # Instantiate MasterAgent
        conversation_id = UUID(request.conversation_id) if request.conversation_id else None
        agent = MasterAgent(user_id, conversation_id)

        # Connect to MCP server
        await agent.connect_mcp()

        # Process message through agent chain
        response = await agent.process_message(request.message)

        # Create or get conversation
        if not request.conversation_id:
            # Create new conversation
            conversation = conv_service.create_conversation()
            conversation_id = conversation.id
        else:
            conversation_id = UUID(request.conversation_id)

        # Save user message
        conv_service.add_message(conversation_id, "user", request.message)

        # Save assistant response
        conv_service.add_message(conversation_id, "assistant", response["message"])

        return ChatResponse(
            message=response["message"],
            conversation_id=str(conversation_id),
            requires_confirmation=response.get("requires_confirmation", False),
            confirmation_details=response.get("confirmation_details")
        )

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {type(e).__name__}: {str(e)}")


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for the authenticated user.

    Args:
        user: Authenticated user from JWT
        db: Database session

    Returns:
        List[ConversationResponse]: User's conversations ordered by updated_at desc
    """
    try:
        user_id = user.id
        service = ConversationService(db, user_id)
        conversations = service.list_conversations()

        return [
            ConversationResponse(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at
            )
            for conv in conversations
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation.

    Args:
        conversation_id: Conversation UUID
        user: Authenticated user from JWT
        db: Database session

    Returns:
        List[MessageResponse]: Messages ordered by created_at asc

    Raises:
        HTTPException: 404 if conversation not found, 403 if unauthorized
    """
    try:
        user_id = user.id
        service = ConversationService(db, user_id)
        messages = service.get_messages(UUID(conversation_id))

        return [
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid conversation_id: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation UUID
        user: Authenticated user from JWT
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if conversation not found, 403 if unauthorized
    """
    try:
        user_id = user.id
        service = ConversationService(db, user_id)
        service.delete_conversation(UUID(conversation_id))

        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }

    except ConversationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid conversation_id: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
