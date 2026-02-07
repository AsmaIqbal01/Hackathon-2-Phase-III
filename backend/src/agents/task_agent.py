"""Task Sub-Agent for handling task-related operations."""


class TaskSubAgent:
    """Sub-agent responsible for routing task operations to MCP tools.

    This agent handles all task-related operations:
    - Creating tasks
    - Listing tasks with filters
    - Updating tasks
    - Completing tasks
    - Deleting tasks (via confirmation agent)

    Attributes:
        master: Reference to the Master Agent
    """

    def __init__(self, master_agent):
        """Initialize TaskSubAgent.

        Args:
            master_agent: Reference to the MasterAgent instance
        """
        self.master = master_agent

    async def handle(self, intent: str, params: dict) -> dict:
        """Route task intent to the appropriate MCP tool.

        Args:
            intent: Task operation intent ("create", "list", "update", "complete", "delete")
            params: Parameters for the tool call

        Returns:
            dict: Result from the MCP tool execution

        Raises:
            RuntimeError: If MCP session is not initialized
            ValueError: If intent is not recognized
        """
        if not self.master.mcp_session:
            raise RuntimeError("MCP session not initialized. Call connect_mcp() first.")

        # Map intents to MCP tool names
        tool_map = {
            "create": "add_task",
            "list": "list_tasks",
            "update": "update_task",
            "complete": "complete_task",
            "delete": "delete_task"
        }

        tool_name = tool_map.get(intent)
        if not tool_name:
            raise ValueError(f"Unknown task intent: {intent}")

        # Check if confirmation is required
        if self.master.confirmation_agent.check_required(tool_name):
            # Return confirmation request instead of executing
            return await self.master.confirmation_agent.request_confirmation(tool_name, params)

        # Execute tool via MCP session
        result = await self.master.mcp_session.call_tool(tool_name, params)

        return result
