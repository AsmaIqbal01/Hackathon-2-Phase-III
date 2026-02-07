"""Master Agent for orchestrating AI-powered task management."""
import json
import os
from typing import List, Dict, Optional
from uuid import UUID
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.agents.confirmation_agent import ConfirmationSubAgent
from src.agents.task_agent import TaskSubAgent
from src.agents.conversation_agent import ConversationSubAgent
from src.services.conversation_service import ConversationService
from src.database import get_db


class MasterAgent:
    """Master Agent responsible for orchestrating all AI operations.

    This agent:
    - Connects to MCP server for tool execution
    - Routes requests to appropriate sub-agents
    - Manages conversation context from database
    - Processes user messages via OpenAI API
    - Handles tool execution and confirmations

    Attributes:
        user_id: Authenticated user's ID
        conversation_id: Current conversation ID (if any)
        client: OpenAI client for API calls
        mcp_session: MCP client session for tool execution
        tools: Available MCP tools
        task_agent: Sub-agent for task operations
        conversation_agent: Sub-agent for conversation queries
        confirmation_agent: Sub-agent for confirmation workflow
    """

    def __init__(self, user_id: str, conversation_id: Optional[UUID] = None):
        """Initialize MasterAgent.

        Args:
            user_id: Authenticated user's ID
            conversation_id: Optional conversation ID to load context
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.client = OpenAI()
        self.mcp_session: Optional[ClientSession] = None
        self.tools = []

        # Instantiate sub-agents
        self.confirmation_agent = ConfirmationSubAgent(self)
        self.task_agent = TaskSubAgent(self)
        self.conversation_agent = ConversationSubAgent(self)

    async def connect_mcp(self):
        """Initialize MCP client connection to the task management server.

        This method:
        - Creates stdio server parameters with user context
        - Connects to MCP server via stdio
        - Lists available tools from the server

        Raises:
            RuntimeError: If connection fails
        """
        # Create server parameters for stdio communication
        server_params = StdioServerParameters(
            command="python",
            args=["backend/src/mcp/server.py"],
            env={"USER_ID": self.user_id}
        )

        # Connect to MCP server
        self.mcp_session = await stdio_client(server_params).__aenter__()

        # List available tools
        self.tools = await self.mcp_session.list_tools()

    def _load_history(self) -> List[dict]:
        """Load conversation history from database.

        Loads the last 20 messages to control token usage while maintaining context.

        Returns:
            List[dict]: Conversation messages in OpenAI format
        """
        if not self.conversation_id:
            return []

        # Get database session
        db = next(get_db())

        # Create ConversationService
        service = ConversationService(db, self.user_id)

        # Get messages for this conversation
        messages = service.get_messages(self.conversation_id)

        # Limit to last 20 messages to control token usage
        recent_messages = messages[-20:] if len(messages) > 20 else messages

        # Convert to OpenAI message format
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]

    def _format_mcp_tools(self, tools) -> List[dict]:
        """Convert MCP tool definitions to OpenAI function calling format.

        Args:
            tools: MCP tool definitions from the server

        Returns:
            List[dict]: Tools in OpenAI function calling format
        """
        # Convert MCP tools to OpenAI format
        openai_tools = []

        for tool in tools:
            # MCP tool schema to OpenAI function schema
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema.get("properties", {}),
                        "required": tool.inputSchema.get("required", [])
                    }
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

    async def _execute_tools(self, tool_calls) -> List[dict]:
        """Execute MCP tools via session.

        Args:
            tool_calls: Tool calls from OpenAI API response

        Returns:
            List[dict]: Results from tool execution
        """
        results = []

        for call in tool_calls:
            tool_name = call.function.name
            arguments = json.loads(call.function.arguments)

            # Check if confirmation is required
            if self.confirmation_agent.check_required(tool_name):
                # Return confirmation request instead of executing
                confirmation = await self.confirmation_agent.request_confirmation(
                    tool_name,
                    arguments
                )
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps(confirmation)
                })
            else:
                # Execute tool via MCP session
                result = await self.mcp_session.call_tool(tool_name, arguments)

                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps(result)
                })

        return results

    def _check_confirmation_needed(self, response) -> bool:
        """Check if response contains confirmation requirements.

        Args:
            response: OpenAI API response

        Returns:
            bool: True if confirmation is needed, False otherwise
        """
        # Check if the response message contains tool calls requiring confirmation
        if not hasattr(response.choices[0].message, 'tool_calls'):
            return False

        if not response.choices[0].message.tool_calls:
            return False

        # Check each tool call
        for call in response.choices[0].message.tool_calls:
            if self.confirmation_agent.check_required(call.function.name):
                return True

        return False

    async def process_message(self, user_message: str) -> dict:
        """Process user message through the agent chain.

        This is the main entry point for message processing:
        1. Load conversation history from DB
        2. Call OpenAI API with user message and available tools
        3. Handle tool calls if present
        4. Continue conversation with tool results
        5. Return final response

        Args:
            user_message: User's natural language message

        Returns:
            dict: Response with message, conversation_id, and confirmation status
        """
        # Load conversation history
        history = self._load_history()

        # Build messages array
        messages = history + [{"role": "user", "content": user_message}]

        # Call OpenAI API with tools
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=self._format_mcp_tools(self.tools),
            tool_choice="auto"
        )

        # Handle tool calls if present
        if response.choices[0].message.tool_calls:
            # Execute tools
            tool_results = await self._execute_tools(response.choices[0].message.tool_calls)

            # Add assistant message with tool calls to history
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
            })

            # Add tool results to history
            for result in tool_results:
                messages.append(result)

            # Continue conversation with tool results
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )

        # Extract final message
        final_message = response.choices[0].message.content

        # Check if confirmation is needed
        requires_confirmation = self._check_confirmation_needed(response)

        # Extract confirmation details if needed
        confirmation_details = None
        if requires_confirmation and response.choices[0].message.tool_calls:
            for call in response.choices[0].message.tool_calls:
                if self.confirmation_agent.check_required(call.function.name):
                    confirmation_details = {
                        "action": call.function.name,
                        "params": json.loads(call.function.arguments)
                    }
                    break

        return {
            "message": final_message,
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "requires_confirmation": requires_confirmation,
            "confirmation_details": confirmation_details
        }
