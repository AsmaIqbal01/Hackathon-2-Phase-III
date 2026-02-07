"""Business logic layer for conversation operations.

ConversationService encapsulates all conversation-related business logic and database operations,
enforcing user ownership and data integrity rules.
"""
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from src.models.conversation import Conversation
from src.models.message import Message
from src.utils.errors import ConversationNotFoundError, UnauthorizedAccessError


class ConversationService:
    """Service layer for conversation CRUD operations with user ownership enforcement.

    This service ensures:
    - All operations are scoped to the authenticated user
    - Cross-user access attempts return 403 Forbidden
    - Database transactions are properly managed
    - Business logic is enforced (validation, ownership, integrity)

    Attributes:
        db: Database session for queries
        user_id: Authenticated user's ID (all operations scoped to this user)
    """

    def __init__(self, db: Session, user_id: str):
        """Initialize ConversationService with database session and user context.

        Args:
            db: SQLModel database session
            user_id: Authenticated user's ID (from JWT or dependency)
        """
        self.db = db
        self.user_id = user_id

    def create_conversation(self, title: Optional[str] = None) -> Conversation:
        """Create a new conversation for the authenticated user.

        Args:
            title: Optional conversation title (auto-generated from first message if None)

        Returns:
            Conversation: Created conversation with auto-generated ID and timestamps
        """
        # Create conversation with user ownership
        conversation = Conversation(
            user_id=self.user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Persist to database
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_conversation(self, conversation_id: UUID) -> Conversation:
        """Get a single conversation by ID.

        Args:
            conversation_id: UUID of the conversation to retrieve

        Returns:
            Conversation: The requested conversation

        Raises:
            ConversationNotFoundError: If conversation doesn't exist for this user
            UnauthorizedAccessError: If conversation belongs to another user (403)

        Security:
            MUST filter by user_id to prevent cross-user access.
            Returns 403 (not 404) for other users' conversations to avoid info disclosure.
        """
        # Query with user_id filter (CRITICAL for security)
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == self.user_id
        )
        conversation = self.db.exec(statement).first()

        if not conversation:
            # Check if conversation exists for another user (to return 403 instead of 404)
            other_user_statement = select(Conversation).where(Conversation.id == conversation_id)
            other_user_conversation = self.db.exec(other_user_statement).first()

            if other_user_conversation:
                # Conversation exists but belongs to another user - return 403
                raise UnauthorizedAccessError(
                    "Access denied: conversation belongs to another user"
                )
            else:
                # Conversation doesn't exist at all - return 404
                raise ConversationNotFoundError(conversation_id=str(conversation_id))

        return conversation

    def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List all conversations for the authenticated user.

        Args:
            limit: Maximum number of conversations to return (default: 50)

        Returns:
            List[Conversation]: List of conversations ordered by updated_at descending

        Note:
            Results are ALWAYS filtered by user_id (enforces user ownership).
        """
        # Query filtered by user_id (CRITICAL for security)
        query = select(Conversation).where(
            Conversation.user_id == self.user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit)

        conversations = self.db.exec(query).all()
        return list(conversations)

    def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: dict = None
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conversation_id: UUID of the conversation
            role: Message role ("user", "assistant", or "system")
            content: Message text content
            metadata: Optional metadata dict (tool calls, confirmations, etc.)

        Returns:
            Message: Created message with auto-generated ID and timestamp

        Raises:
            ConversationNotFoundError: If conversation doesn't exist for this user
            UnauthorizedAccessError: If conversation belongs to another user
        """
        # Validate conversation ownership (will raise error if not found or unauthorized)
        conversation = self.get_conversation(conversation_id)

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata or {},
            created_at=datetime.utcnow()
        )

        # Persist to database
        self.db.add(message)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()
        self.db.add(conversation)

        self.db.commit()
        self.db.refresh(message)

        return message

    def get_messages(self, conversation_id: UUID) -> List[Message]:
        """Get all messages in a conversation.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            List[Message]: List of messages ordered by created_at ascending

        Raises:
            ConversationNotFoundError: If conversation doesn't exist for this user
            UnauthorizedAccessError: If conversation belongs to another user

        Note:
            Validates conversation ownership before retrieving messages.
        """
        # Validate conversation ownership (will raise error if not found or unauthorized)
        self.get_conversation(conversation_id)

        # Query messages ordered by creation time
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        messages = self.db.exec(query).all()
        return list(messages)

    def delete_conversation(self, conversation_id: UUID) -> None:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: UUID of the conversation to delete

        Raises:
            ConversationNotFoundError: If conversation doesn't exist for this user
            UnauthorizedAccessError: If conversation belongs to another user

        Note:
            This is a hard delete (removes from database).
            Messages are cascade deleted via foreign key constraint.
        """
        # Validate conversation ownership (will raise error if not found or unauthorized)
        conversation = self.get_conversation(conversation_id)

        # Delete all messages in the conversation first
        delete_messages_query = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.db.exec(delete_messages_query).all()
        for message in messages:
            self.db.delete(message)

        # Delete the conversation
        self.db.delete(conversation)
        self.db.commit()
