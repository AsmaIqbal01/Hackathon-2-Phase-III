"""Confirmation Sub-Agent for handling destructive operations."""
from typing import Optional


class ConfirmationSubAgent:
    """Sub-agent responsible for handling confirmation workflow for destructive operations.

    This agent:
    - Identifies operations that require user confirmation
    - Generates confirmation prompts
    - Executes confirmed actions via MCP tools

    Attributes:
        master: Reference to the Master Agent
        REQUIRES_CONFIRMATION: List of tool names requiring confirmation
    """

    # Tools that require user confirmation before execution
    REQUIRES_CONFIRMATION = ["delete_task", "delete_conversation"]

    def __init__(self, master_agent):
        """Initialize ConfirmationSubAgent.

        Args:
            master_agent: Reference to the MasterAgent instance
        """
        self.master = master_agent

    def check_required(self, tool_name: str) -> bool:
        """Check if a tool requires confirmation.

        Args:
            tool_name: Name of the MCP tool to check

        Returns:
            bool: True if confirmation is required, False otherwise
        """
        return tool_name in self.REQUIRES_CONFIRMATION

    async def request_confirmation(self, tool_name: str, params: dict) -> dict:
        """Generate a confirmation prompt for the user.

        Args:
            tool_name: Name of the tool requiring confirmation
            params: Parameters for the tool call

        Returns:
            dict: Confirmation request with prompt and action details
        """
        # Generate human-readable prompt based on tool name
        prompts = {
            "delete_task": f"Are you sure you want to delete the task with ID {params.get('task_id')}?",
            "delete_conversation": f"Are you sure you want to delete the entire conversation with ID {params.get('conversation_id')}? This will remove all messages."
        }

        prompt = prompts.get(tool_name, f"Are you sure you want to {tool_name}?")

        return {
            "requires_confirmation": True,
            "action": tool_name,
            "params": params,
            "prompt": prompt
        }

    async def execute_confirmed(self, action: str, params: dict) -> dict:
        """Execute a confirmed action via MCP tools.

        This method is called after the user has confirmed the action.

        Args:
            action: Name of the tool to execute
            params: Parameters for the tool call

        Returns:
            dict: Result from the MCP tool execution
        """
        if not self.master.mcp_session:
            raise RuntimeError("MCP session not initialized. Call connect_mcp() first.")

        # Execute the tool via MCP session
        result = await self.master.mcp_session.call_tool(action, params)

        return result
