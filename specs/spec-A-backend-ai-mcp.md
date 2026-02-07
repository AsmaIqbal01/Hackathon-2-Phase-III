# Spec A: Backend Intelligence & AI Integration (MCP + OpenAI Agents)

**Version:** 1.0
**Status:** Draft
**Owner:** Phase III Backend Team
**Context:** Phase III extends Phase II (CRUD + Auth) with conversational AI task management using OpenAI Agents SDK and Model Context Protocol (MCP).

---

## 1. Architecture Overview

```
Client → FastAPI Endpoint → Master Agent → MCP Server → Database
                                ↓
                          Sub-Agents (Task, Conversation, Confirmation)
```

### 1.1 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **FastAPI Endpoint** | Stateless HTTP interface, auth validation | FastAPI |
| **Master Agent** | Request orchestration, sub-agent coordination | OpenAI Agents SDK |
| **Sub-Agents** | Domain-specific logic (tasks, conversations, confirmations) | OpenAI Agents SDK |
| **MCP Server** | Structured tool interface for DB operations | Official MCP SDK (Python) |
| **Database** | Persistence layer (Tasks, Conversations, Messages) | PostgreSQL (Neon) / SQLite (dev) |

### 1.2 Stateless Request Lifecycle

```
1. Client sends POST /chat with { message, user_id, conversation_id? }
2. FastAPI validates JWT, extracts user_id
3. Load conversation history from DB (if conversation_id provided)
4. Instantiate Master Agent with MCP tools + conversation context
5. Master Agent processes message:
   a. Routes to Task Sub-Agent (for task operations)
   b. Routes to Conversation Sub-Agent (for context/history queries)
   c. Routes to Confirmation Sub-Agent (for destructive actions)
6. MCP tools execute database operations via TaskService / ConversationService
7. Persist new message to DB
8. Return response { message, conversation_id, requires_confirmation? }
9. Agent state discarded (stateless)
```

**Critical:** No agent state persists between requests. All context loaded from DB per request.

---

## 2. Reused Phase II Components

### 2.1 Database Models (Unchanged)

From `backend/src/models/`:

| Model | Fields | Usage |
|-------|--------|-------|
| **Task** | `id, user_id, title, description, status, priority, tags, created_at, updated_at` | Task entity (already implemented) |
| **User** | `id, email, password_hash, created_at, updated_at` | User entity (already implemented) |
| **RefreshToken** | `id, user_id, token, expires_at` | Auth token (already implemented) |

### 2.2 Business Logic (Unchanged)

From `backend/src/services/task_service.py`:

- `TaskService.create_task(data: TaskCreate) -> Task`
- `TaskService.list_tasks(status?, priority?, tags?, sort_by?) -> List[Task]`
- `TaskService.get_task_by_id(task_id: UUID) -> Task`
- `TaskService.update_task(task_id: UUID, data: TaskUpdate) -> Task`
- `TaskService.delete_task(task_id: UUID) -> None`

**Design Rule:** MCP tools MUST call TaskService methods. Never bypass service layer.

---

## 3. New Phase III Components

### 3.1 New Database Models

Add to `backend/src/models/`:

#### **Conversation Model**
```python
class Conversation(SQLModel, table=True):
    """Conversation thread linking user messages."""
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: Optional[str] = Field(default=None, max_length=255)  # Auto-generated from first message
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### **Message Model**
```python
class Message(SQLModel, table=True):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=50)  # "user" | "assistant" | "system"
    content: str = Field(nullable=False)  # Message text
    metadata: dict = Field(default={}, sa_column=Column(JSON))  # Tool calls, confirmations, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("idx_messages_conversation", "conversation_id", "created_at"),
    )
```

### 3.2 New Services

#### **ConversationService** (`backend/src/services/conversation_service.py`)

```python
class ConversationService:
    def __init__(self, db: Session, user_id: str): ...

    def create_conversation(self, title: Optional[str] = None) -> Conversation
    def get_conversation(self, conversation_id: UUID) -> Conversation
    def list_conversations(self, limit: int = 50) -> List[Conversation]
    def add_message(self, conversation_id: UUID, role: str, content: str, metadata: dict = {}) -> Message
    def get_messages(self, conversation_id: UUID) -> List[Message]
    def delete_conversation(self, conversation_id: UUID) -> None
```

**Validation:**
- Enforce user ownership (same as TaskService)
- Raise `UnauthorizedAccessError` for cross-user access
- Auto-generate title from first user message if not provided

---

## 4. MCP Server Architecture

### 4.1 MCP Server Setup

File: `backend/src/mcp/server.py`

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("task-management-mcp")

# Tool registration
@app.tool()
async def add_task(title: str, description: str = "", ...) -> dict:
    """Create a new task. Returns task ID and confirmation."""
    # Implementation delegates to TaskService
    ...

@app.tool()
async def list_tasks(status: str = None, ...) -> dict:
    """List tasks with optional filters."""
    ...

@app.tool()
async def complete_task(task_id: str) -> dict:
    """Mark a task as completed."""
    ...

@app.tool()
async def update_task(task_id: str, **kwargs) -> dict:
    """Update task fields."""
    ...

@app.tool()
async def delete_task(task_id: str) -> dict:
    """Delete a task (requires confirmation)."""
    ...

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
```

### 4.2 MCP Tool Definitions

| Tool Name | Parameters | Returns | Confirmation Required |
|-----------|-----------|---------|----------------------|
| `add_task` | `title: str, description?: str, priority?: str, tags?: str[]` | `{ success: bool, task_id: UUID, message: str }` | No |
| `list_tasks` | `status?: str, priority?: str, tags?: str[], sort_by?: str` | `{ tasks: Task[], count: int }` | No |
| `complete_task` | `task_id: str` | `{ success: bool, task: Task }` | No |
| `update_task` | `task_id: str, title?: str, description?: str, status?: str, priority?: str, tags?: str[]` | `{ success: bool, task: Task }` | No |
| `delete_task` | `task_id: str` | `{ success: bool, message: str }` | **Yes** |

### 4.3 MCP-to-Service Integration

```python
# Inside MCP tool handler
@app.tool()
async def add_task(title: str, description: str = "", ...):
    db = next(get_db())  # Get session
    user_id = get_context_user_id()  # From MCP context
    service = TaskService(db, user_id)

    task = service.create_task(TaskCreate(
        title=title,
        description=description,
        ...
    ))

    return {"success": True, "task_id": str(task.id), "message": f"Created task: {task.title}"}
```

**Design Rules:**
- MCP tools MUST use TaskService for all DB operations
- Never execute raw SQL from MCP tools
- All errors propagate as MCP tool errors (JSON structure)

---

## 5. OpenAI Agents SDK Architecture

### 5.1 Master Agent

File: `backend/src/agents/master_agent.py`

```python
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MasterAgent:
    def __init__(self, user_id: str, conversation_id: Optional[UUID] = None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.client = OpenAI()
        self.mcp_session: Optional[ClientSession] = None

    async def connect_mcp(self):
        """Initialize MCP client connection."""
        server_params = StdioServerParameters(
            command="python",
            args=["backend/src/mcp/server.py"],
            env={"USER_ID": self.user_id}
        )

        self.mcp_session = await stdio_client(server_params).__aenter__()
        self.tools = await self.mcp_session.list_tools()

    async def process_message(self, user_message: str) -> dict:
        """
        Process user message with agent chain:
        1. Load conversation history from DB
        2. Detect intent (task operation vs. query vs. confirmation)
        3. Route to appropriate sub-agent
        4. Execute MCP tools via sub-agent
        5. Persist message to DB
        """
        history = self._load_history()

        messages = history + [{"role": "user", "content": user_message}]

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=self._format_mcp_tools(self.tools),
            tool_choice="auto"
        )

        # Handle tool calls
        if response.choices[0].message.tool_calls:
            tool_results = await self._execute_tools(response.choices[0].message.tool_calls)
            # Continue conversation with tool results
            ...

        return {
            "message": response.choices[0].message.content,
            "conversation_id": str(self.conversation_id),
            "requires_confirmation": self._check_confirmation_needed(response)
        }

    def _load_history(self) -> List[dict]:
        """Load conversation history from DB."""
        if not self.conversation_id:
            return []

        db = next(get_db())
        service = ConversationService(db, self.user_id)
        messages = service.get_messages(self.conversation_id)

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def _execute_tools(self, tool_calls) -> List[dict]:
        """Execute MCP tools via session."""
        results = []
        for call in tool_calls:
            result = await self.mcp_session.call_tool(
                call.function.name,
                arguments=json.loads(call.function.arguments)
            )
            results.append(result)
        return results
```

### 5.2 Sub-Agents

#### **Task Sub-Agent**
Handles: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`

```python
class TaskSubAgent:
    def __init__(self, master_agent: MasterAgent):
        self.master = master_agent

    async def handle(self, intent: str, params: dict) -> dict:
        """Route task intent to appropriate MCP tool."""
        tool_map = {
            "create": "add_task",
            "list": "list_tasks",
            "update": "update_task",
            "complete": "complete_task",
            "delete": "delete_task"
        }

        tool_name = tool_map.get(intent)
        result = await self.master.mcp_session.call_tool(tool_name, params)
        return result
```

#### **Conversation Sub-Agent**
Handles: Conversation history queries, context retrieval

```python
class ConversationSubAgent:
    def __init__(self, master_agent: MasterAgent):
        self.master = master_agent

    async def handle(self, query: str) -> dict:
        """Query conversation history."""
        history = self.master._load_history()
        # Use semantic search or simple filtering
        ...
```

#### **Confirmation Sub-Agent**
Handles: Destructive operations requiring explicit user consent

```python
class ConfirmationSubAgent:
    REQUIRES_CONFIRMATION = ["delete_task", "delete_conversation"]

    def check_required(self, tool_name: str) -> bool:
        return tool_name in self.REQUIRES_CONFIRMATION

    async def request_confirmation(self, tool_name: str, params: dict) -> dict:
        """Return confirmation prompt to user."""
        return {
            "requires_confirmation": True,
            "action": tool_name,
            "params": params,
            "prompt": f"Are you sure you want to {tool_name}?"
        }

    async def execute_confirmed(self, action: str, params: dict) -> dict:
        """Execute action after user confirms."""
        result = await self.master.mcp_session.call_tool(action, params)
        return result
```

---

## 6. FastAPI Endpoint

### 6.1 Chat Endpoint

File: `backend/src/api/routes/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from src.auth.authenticator import get_current_user
from src.agents.master_agent import MasterAgent
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    confirm_action: Optional[dict] = None  # For confirmation responses

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    requires_confirmation: bool = False
    confirmation_details: Optional[dict] = None

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Stateless chat endpoint.

    Flow:
    1. Validate JWT (via get_current_user)
    2. Instantiate MasterAgent with user_id + conversation_id
    3. Process message through agent chain
    4. Persist message to DB
    5. Return response
    """
    user_id = user["user_id"]

    # Handle confirmation responses
    if request.confirm_action:
        agent = MasterAgent(user_id, UUID(request.conversation_id))
        await agent.connect_mcp()
        result = await agent.confirmation_agent.execute_confirmed(
            request.confirm_action["action"],
            request.confirm_action["params"]
        )
        return ChatResponse(
            message=result.get("message", "Action completed."),
            conversation_id=request.conversation_id,
            requires_confirmation=False
        )

    # Normal message processing
    agent = MasterAgent(user_id, UUID(request.conversation_id) if request.conversation_id else None)
    await agent.connect_mcp()

    response = await agent.process_message(request.message)

    # Persist message to DB
    db = next(get_db())
    conv_service = ConversationService(db, user_id)

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
```

### 6.2 Conversation Management Endpoints

```python
@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(user: dict = Depends(get_current_user)):
    """List all conversations for authenticated user."""
    db = next(get_db())
    service = ConversationService(db, user["user_id"])
    conversations = service.list_conversations()
    return conversations

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Get all messages in a conversation."""
    db = next(get_db())
    service = ConversationService(db, user["user_id"])
    messages = service.get_messages(UUID(conversation_id))
    return messages

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a conversation and all messages."""
    db = next(get_db())
    service = ConversationService(db, user["user_id"])
    service.delete_conversation(UUID(conversation_id))
    return {"success": True, "message": "Conversation deleted"}
```

---

## 7. Error Handling

### 7.1 Error Categories

| Error Type | HTTP Status | MCP Behavior | Agent Behavior |
|-----------|-------------|--------------|----------------|
| **Authentication Error** | 401 | N/A | Reject request at FastAPI level |
| **Authorization Error** | 403 | Tool returns error | Agent surfaces as message |
| **Resource Not Found** | 404 | Tool returns error | Agent surfaces as message |
| **Validation Error** | 422 | Tool returns error | Agent surfaces as message |
| **Tool Execution Error** | 500 | Tool returns error | Agent retries or surfaces error |
| **MCP Connection Error** | 503 | Connection fails | Return service unavailable |

### 7.2 Error Propagation Flow

```
DB Error → TaskService raises → MCP tool catches → Returns error JSON → Agent interprets → Natural language response
```

Example:
```python
# TaskService raises
raise TaskNotFoundError(task_id=task_id)

# MCP tool catches
try:
    task = service.get_task_by_id(UUID(task_id))
except TaskNotFoundError as e:
    return {"success": False, "error": str(e)}

# Agent interprets
"I couldn't find a task with that ID. Please check and try again."
```

### 7.3 Confirmation Handling

Destructive operations require two-step confirmation:

```
User: "Delete task abc-123"
Agent: {
  "message": "Are you sure you want to delete task 'Fix bug'?",
  "requires_confirmation": true,
  "confirmation_details": {
    "action": "delete_task",
    "params": {"task_id": "abc-123"}
  }
}

User: {"confirm_action": {"action": "delete_task", "params": {"task_id": "abc-123"}}}
Agent: {
  "message": "Task deleted successfully.",
  "requires_confirmation": false
}
```

---

## 8. Stateless Design Constraints

### 8.1 No Persistent Agent State

**Prohibited:**
- In-memory conversation buffers
- Agent-side caching of tasks
- Session-specific agent instances

**Required:**
- Full context loaded from DB per request
- Agent instances instantiated and discarded per request
- All state persisted to DB immediately

### 8.2 Context Loading Strategy

```python
def _load_history(self) -> List[dict]:
    """Load last N messages from DB (default: 20)."""
    messages = self.conv_service.get_messages(self.conversation_id)

    # Limit to last 20 messages to control token usage
    recent_messages = messages[-20:]

    return [
        {"role": msg.role, "content": msg.content}
        for msg in recent_messages
    ]
```

**Trade-offs:**
- Increased DB queries per request (acceptable for Phase III scale)
- Simplified deployment (no agent state management)
- Easier horizontal scaling (any instance handles any request)

---

## 9. Dependencies & Technology Stack

### 9.1 New Dependencies

Add to `backend/requirements.txt`:

```
openai>=1.0.0                    # OpenAI Agents SDK
mcp>=1.0.0                       # Model Context Protocol SDK
```

### 9.2 Environment Variables

Add to `.env`:

```
OPENAI_API_KEY=sk-...           # OpenAI API key
MCP_SERVER_HOST=localhost       # MCP server host (for stdio, not needed)
```

### 9.3 Technology Versions

| Component | Version | Justification |
|-----------|---------|---------------|
| **FastAPI** | 0.104+ | Already used in Phase II |
| **SQLModel** | 0.0.14+ | Already used in Phase II |
| **OpenAI SDK** | 1.0+ | Latest Agents SDK support |
| **MCP SDK** | 1.0+ | Official Python implementation |
| **PostgreSQL** | 15+ | Production DB (Neon) |
| **SQLite** | 3.40+ | Local development |

---

## 10. Out of Scope (Phase III)

**Explicitly excluded:**
- Frontend UI (exists in Phase II, not modified)
- Real-time streaming responses (use standard HTTP)
- Multi-turn agent planning (single-turn per request)
- Custom NLP models (use OpenAI only)
- Rate limiting beyond Phase II auth
- Advanced conversation analytics
- Conversation search/indexing
- Multi-user conversations
- Agent training or fine-tuning
- Tool usage analytics
- Conversation export/import

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Coverage targets:**
- TaskService methods (already tested in Phase II)
- ConversationService methods (new)
- MCP tool handlers (new)
- Agent routing logic (new)

### 11.2 Integration Tests

**Scenarios:**
1. End-to-end chat flow (user message → DB → MCP → agent → response)
2. Confirmation workflow (request → confirm → execute)
3. Multi-turn conversation persistence
4. Error propagation (DB error → agent message)

### 11.3 Test Data

Reuse Phase II fixtures:
- User fixtures (`test_user`, `test_user_2`)
- Task fixtures (`test_task`, `completed_task`)

New fixtures:
- Conversation fixtures
- Message fixtures
- MCP mock tools

---

## 12. Deployment Notes

### 12.1 MCP Server Deployment

**Local Development:**
```bash
# Run MCP server in separate process
python backend/src/mcp/server.py
```

**Production:**
- MCP server runs as subprocess of FastAPI app
- Stdio communication (no network layer)
- Single instance per FastAPI worker

### 12.2 Database Migrations

```bash
# Create new tables
alembic revision --autogenerate -m "Add Conversation and Message models"
alembic upgrade head
```

---

## 13. Success Criteria

**Functional:**
- ✅ User can send conversational task commands
- ✅ Agent correctly routes to task operations
- ✅ Conversation history persists across requests
- ✅ Destructive actions require confirmation
- ✅ Errors surface as natural language responses

**Non-Functional:**
- ✅ P95 response time < 3s (includes OpenAI API latency)
- ✅ No agent state leaks between requests
- ✅ All DB operations use service layer
- ✅ 100% test coverage for new services
- ✅ No Phase II regressions

---

## 14. Implementation Sequence

1. **Database Models** (Conversation, Message)
2. **ConversationService** (CRUD operations)
3. **MCP Server** (tool definitions + TaskService integration)
4. **Master Agent** (MCP client + conversation loading)
5. **Sub-Agents** (Task, Conversation, Confirmation)
6. **FastAPI Endpoint** (`POST /chat`)
7. **Conversation Management Endpoints** (list, get messages, delete)
8. **Integration Tests**
9. **Documentation**

---

## 15. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **OpenAI API latency** | Slow response times | Set timeout (10s), surface errors gracefully |
| **MCP tool errors** | Agent confusion | Structured error JSON, agent retry logic |
| **Context window limits** | Conversation history truncation | Load last 20 messages only |
| **Confirmation bypass** | Accidental deletions | Enforce confirmation check in MCP tools |
| **Cross-user access** | Security breach | Enforce user_id filtering in all services |

---

## Appendix A: Phase II → Phase III Delta

### What's Reused (Unchanged)
- Task, User, RefreshToken models
- TaskService CRUD methods
- Authentication middleware
- Database connection logic
- FastAPI structure

### What's New (Phase III)
- Conversation, Message models
- ConversationService
- MCP server + tools
- OpenAI Agents SDK integration
- Master Agent + Sub-Agents
- Chat endpoint (`POST /chat`)

### What's Modified
- `database.py`: Import new models
- `main.py`: Register chat router
- `requirements.txt`: Add OpenAI + MCP SDKs

---

**End of Spec A**
