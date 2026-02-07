"""Conversation Sub-Agent for handling conversation history queries."""
from typing import List, Dict


class ConversationSubAgent:
    """Sub-agent responsible for conversation history queries and context management.

    This agent handles:
    - Querying conversation history
    - Filtering messages by criteria
    - Context retrieval for the Master Agent

    Attributes:
        master: Reference to the Master Agent
    """

    def __init__(self, master_agent):
        """Initialize ConversationSubAgent.

        Args:
            master_agent: Reference to the MasterAgent instance
        """
        self.master = master_agent

    async def handle(self, query: str) -> dict:
        """Handle conversation history queries.

        For Phase III, this implements simple filtering of conversation history.
        Future versions could add semantic search or more advanced querying.

        Args:
            query: Natural language query about conversation history

        Returns:
            dict: Query results with relevant messages
        """
        # Load conversation history
        history = self.master._load_history()

        # Simple keyword-based filtering for Phase III
        # (No semantic search - keep it simple)
        query_lower = query.lower()

        # Filter messages that contain query keywords
        relevant_messages = [
            msg for msg in history
            if query_lower in msg.get("content", "").lower()
        ]

        return {
            "success": True,
            "query": query,
            "matches": len(relevant_messages),
            "messages": relevant_messages
        }

    def get_recent_context(self, limit: int = 5) -> List[Dict]:
        """Get recent conversation context.

        Args:
            limit: Number of recent messages to return (default: 5)

        Returns:
            List[Dict]: Recent messages from conversation history
        """
        history = self.master._load_history()

        # Return last N messages
        return history[-limit:] if len(history) > limit else history
