---
description: "Task list for backend AI + MCP integration implementation"
---

# Tasks: Backend AI + MCP Integration

**Input**: Design documents from `/specs/backend-ai-mcp/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: Included in Phase 6 (unit + integration tests as specified in plan.md)

**Organization**: Tasks organized by technical layer (architectural phases from plan.md), enabling systematic bottom-up implementation.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Phase III adds: `backend/src/mcp/`, `backend/src/agents/`, `backend/src/api/routes/chat.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and verify Phase II baseline

- [X] T001 Add openai>=1.0.0 and mcp>=1.0.0 to backend/requirements.txt
- [X] T002 Add OPENAI_API_KEY to .env and .env.example with documentation
- [X] T003 Run pip install -r backend/requirements.txt and verify no conflicts
- [X] T004 Run pytest backend/tests/ to verify Phase II baseline (all tests pass)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and service layer for conversation management

**⚠️ CRITICAL**: These models and services are required by all AI/MCP components

### Database Models

- [X] T005 [P] Create Conversation model in backend/src/models/conversation.py with fields: id (UUID), user_id (str, indexed), title (Optional[str]), created_at, updated_at
- [X] T006 [P] Create Message model in backend/src/models/message.py with fields: id (UUID), conversation_id (FK), role (str), content (str), metadata (JSON), created_at, and composite index idx_messages_conversation
- [X] T007 Update backend/src/models/__init__.py to import and export Conversation and Message
- [X] T008 Update backend/src/database.py imports (line 4) to include Conversation and Message
- [X] T009 Run database migration using SQLModel.metadata.create_all or alembic revision --autogenerate -m "Add Conversation and Message models" then alembic upgrade head

### ConversationService

- [X] T010 Add ConversationNotFoundError to backend/src/utils/errors.py following TaskNotFoundError pattern
- [X] T011 Create ConversationService class in backend/src/services/conversation_service.py with constructor __init__(self, db: Session, user_id: str)
- [X] T012 [P] Implement create_conversation method in backend/src/services/conversation_service.py
- [X] T013 [P] Implement get_conversation method with user ownership enforcement in backend/src/services/conversation_service.py
- [X] T014 [P] Implement list_conversations method (limit=50, ordered by updated_at desc) in backend/src/services/conversation_service.py
- [X] T015 Implement add_message method with conversation ownership validation in backend/src/services/conversation_service.py
- [X] T016 Implement get_messages method (ordered by created_at asc) in backend/src/services/conversation_service.py
- [X] T017 Implement delete_conversation method with cascade delete in backend/src/services/conversation_service.py

**Checkpoint**: Foundation ready - MCP and agent components can now be implemented

---

## Phase 3: MCP Server Layer

**Purpose**: Implement MCP server with 5 task operation tools

### MCP Infrastructure

- [X] T018 Create backend/src/mcp/__init__.py (empty file to make module)
- [X] T019 Create MCP context manager in backend/src/mcp/context.py with get_context_user_id() and get_db_session() functions
- [X] T020 Initialize MCP Server in backend/src/mcp/server.py: import Server and stdio_server, create app = Server("task-management-mcp"), stub async def main()

### MCP Tools (Task Operations)

- [X] T021 [P] Implement add_task tool in backend/src/mcp/server.py with signature async def add_task(title, description="", priority="medium", tags=[]) delegating to TaskService.create_task
- [X] T022 [P] Implement list_tasks tool in backend/src/mcp/server.py with signature async def list_tasks(status=None, priority=None, tags=None, sort_by=None) delegating to TaskService.list_tasks
- [X] T023 [P] Implement complete_task tool in backend/src/mcp/server.py with signature async def complete_task(task_id) delegating to TaskService.update_task with status="completed"
- [X] T024 [P] Implement update_task tool in backend/src/mcp/server.py with signature async def update_task(task_id, title=None, description=None, status=None, priority=None, tags=None) delegating to TaskService.update_task
- [X] T025 [P] Implement delete_task tool in backend/src/mcp/server.py with signature async def delete_task(task_id) delegating to TaskService.delete_task
- [X] T026 Complete MCP main() function in backend/src/mcp/server.py: async with stdio_server() as (read_stream, write_stream): await app.run(...) and add if __name__ == "__main__": asyncio.run(main())

**Checkpoint**: MCP server can run standalone and expose task tools

---

## Phase 4: OpenAI Agents Layer

**Purpose**: Implement Master Agent with sub-agents for orchestration

### Sub-Agents

- [X] T027 Create backend/src/agents/__init__.py (empty file to make module)
- [X] T028 Create ConfirmationSubAgent in backend/src/agents/confirmation_agent.py with REQUIRES_CONFIRMATION constant, check_required(), request_confirmation(), and execute_confirmed() methods
- [X] T029 Create TaskSubAgent in backend/src/agents/task_agent.py with __init__(self, master_agent) and async handle(intent, params) method with intent-to-tool mapping
- [X] T030 Create ConversationSubAgent in backend/src/agents/conversation_agent.py with __init__(self, master_agent) and async handle(query) method for history queries

### Master Agent

- [X] T031 Create MasterAgent class in backend/src/agents/master_agent.py with __init__(self, user_id, conversation_id=None) and instantiate all sub-agents
- [X] T032 Implement connect_mcp() method in backend/src/agents/master_agent.py: create StdioServerParameters, connect via stdio_client, list tools
- [X] T033 Implement _load_history() method in backend/src/agents/master_agent.py: return empty list if no conversation_id, else load last 20 messages from DB via ConversationService
- [X] T034 Implement _format_mcp_tools() method in backend/src/agents/master_agent.py: convert MCP tool definitions to OpenAI function calling format
- [X] T035 Implement _execute_tools() method in backend/src/agents/master_agent.py: loop through tool_calls, check confirmation requirements, call mcp_session.call_tool()
- [X] T036 Implement _check_confirmation_needed() method in backend/src/agents/master_agent.py: check if any tool call requires confirmation
- [X] T037 Implement process_message() method in backend/src/agents/master_agent.py: load history, call OpenAI API with tools, handle tool_calls, return response dict with message/conversation_id/requires_confirmation

**Checkpoint**: Master Agent can process messages, route to MCP tools, and handle confirmations

---

## Phase 5: FastAPI Chat Endpoints

**Purpose**: Stateless HTTP interface for conversational AI

### Schemas

- [ ] T038 Create backend/src/schemas/chat_schemas.py with ChatRequest (message, conversation_id, confirm_action), ChatResponse (message, conversation_id, requires_confirmation, confirmation_details), ConversationResponse (id, title, created_at, updated_at), MessageResponse (id, role, content, created_at) schemas

### Chat Router

- [ ] T039 Create chat router in backend/src/api/routes/chat.py with imports and router = APIRouter(prefix="/chat", tags=["chat"])
- [ ] T040 Implement POST /chat endpoint part 1 in backend/src/api/routes/chat.py: handle confirmation responses (if request.confirm_action exists, execute via agent.confirmation_agent.execute_confirmed)
- [ ] T041 Implement POST /chat endpoint part 2 in backend/src/api/routes/chat.py: normal message processing (instantiate MasterAgent, connect MCP, process message)
- [ ] T042 Implement POST /chat endpoint part 3 in backend/src/api/routes/chat.py: persistence logic (create or get conversation, save user message, save assistant response via ConversationService.add_message)
- [ ] T043 [P] Implement GET /conversations endpoint in backend/src/api/routes/chat.py: list user's conversations via ConversationService.list_conversations()
- [ ] T044 [P] Implement GET /conversations/{conversation_id}/messages endpoint in backend/src/api/routes/chat.py: get conversation messages via ConversationService.get_messages()
- [ ] T045 [P] Implement DELETE /conversations/{conversation_id} endpoint in backend/src/api/routes/chat.py: delete conversation via ConversationService.delete_conversation()
- [ ] T046 Register chat router in backend/src/main.py: import chat_router and call app.include_router(chat_router)

**Checkpoint**: Chat endpoints functional - users can send messages, view history, manage conversations

---

## Phase 6: Testing

**Purpose**: Unit and integration tests for new components

### Test Fixtures

- [ ] T047 Create conversation fixtures in backend/tests/fixtures/conversation_fixtures.py with test_conversation, test_message, test_conversation_with_messages following task_fixtures.py pattern

### Unit Tests

- [ ] T048 [P] Write ConversationService unit tests in backend/tests/unit/test_conversation_service.py: test_create_conversation, test_get_conversation, test_list_conversations, test_add_message, test_get_messages, test_delete_conversation, test_unauthorized_access (7 tests)
- [ ] T049 [P] Write MCP tool unit tests in backend/tests/unit/test_mcp_tools.py: mock MCP context and DB session, test each of 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) plus error handling
- [ ] T050 [P] Write Master Agent unit tests in backend/tests/unit/test_master_agent.py: mock OpenAI client and MCP session, test _load_history, _format_tools, _execute_tools, _check_confirmation_needed, confirmation workflow

### Integration Tests

- [ ] T051 Write end-to-end chat integration tests in backend/tests/integration/test_chat_e2e.py: test_chat_create_task (full flow), test_chat_with_history (multi-turn), test_chat_confirmation_workflow (delete with confirmation), test_conversation_persistence (messages saved to DB)
- [ ] T052 Run pytest backend/tests/ -v --cov=backend/src and verify 100% coverage for new services (ConversationService, MCP tools, Master Agent) and no Phase II regressions

**Checkpoint**: All tests passing - code quality verified

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final checks

- [ ] T053 [P] Update README.md or backend/docs/api.md with /chat endpoint documentation, environment variables (OPENAI_API_KEY), and MCP server usage
- [ ] T054 Verify stateless design: manually send chat request, restart server, send follow-up and verify context loads from DB with no agent state persisting
- [ ] T055 Verify Phase II baseline unchanged: test Phase II frontend connects to CRUD endpoints, task CRUD operations work via REST API, auth flow unchanged
- [ ] T056 Performance baseline: manually measure chat endpoint P95 latency with target < 3s including OpenAI API call, document results in specs/backend-ai-mcp/performance.md (optional)
- [ ] T057 Final validation checklist: verify all 5 MCP tools implemented and tested, Master Agent + 3 sub-agents working, Conversation/Message models in DB, ConversationService enforces user ownership, chat endpoint stateless, confirmation workflow functional, all tests passing, no Phase II regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T004) - BLOCKS Phases 3-5
- **MCP Server (Phase 3)**: Depends on Foundational completion (T017) - Database models and services must exist
- **Agents (Phase 4)**: Depends on MCP Server completion (T026) - Agents call MCP tools
- **FastAPI Endpoints (Phase 5)**: Depends on Agents completion (T037) - Endpoints instantiate MasterAgent
- **Testing (Phase 6)**: Depends on Endpoints completion (T046) - Tests require full implementation
- **Polish (Phase 7)**: Depends on Testing completion (T052) - Final validation after tests pass

### Critical Path

```
T001 → T004 → T009 → T017 → T026 → T037 → T046 → T052 → T057
```

**Linear backbone**: Setup → Foundation → MCP → Agents → API → Tests → Validation

### Within Each Phase

**Phase 2 (Foundational)**:
- T005-T006 (models) can run in parallel [P]
- T012-T014 (service methods) can run in parallel [P] after T011

**Phase 3 (MCP Server)**:
- T021-T025 (MCP tools) can run in parallel [P] after T020

**Phase 4 (Agents)**:
- T028-T030 (sub-agents) run sequentially (each depends on previous for pattern)
- T032-T036 (Master Agent methods) run sequentially (each builds on previous)

**Phase 5 (FastAPI)**:
- T043-T045 (conversation management endpoints) can run in parallel [P] after T042

**Phase 6 (Testing)**:
- T048-T050 (unit tests) can run in parallel [P] after T047
- T051 (integration) depends on T048-T050 completion

**Phase 7 (Polish)**:
- T053 (docs) can run in parallel [P] with T054-T056
- T057 (final checklist) depends on all previous tasks

### Parallel Opportunities

```bash
# Phase 2: Database models
T005 (Conversation model) + T006 (Message model)

# Phase 2: Service methods
T012 (create_conversation) + T013 (get_conversation) + T014 (list_conversations)

# Phase 3: MCP tools
T021 (add_task) + T022 (list_tasks) + T023 (complete_task) + T024 (update_task) + T025 (delete_task)

# Phase 5: Conversation endpoints
T043 (GET /conversations) + T044 (GET /conversations/{id}/messages) + T045 (DELETE /conversations/{id})

# Phase 6: Unit tests
T048 (ConversationService tests) + T049 (MCP tool tests) + T050 (Master Agent tests)

# Phase 7: Documentation and validation
T053 (docs) + T054 (stateless verify) + T055 (Phase II verify) + T056 (performance)
```

---

## Parallel Example: Phase 3 (MCP Tools)

```bash
# After T020 (MCP server initialized), launch all 5 tools together:
Task: "Implement add_task tool in backend/src/mcp/server.py..."
Task: "Implement list_tasks tool in backend/src/mcp/server.py..."
Task: "Implement complete_task tool in backend/src/mcp/server.py..."
Task: "Implement update_task tool in backend/src/mcp/server.py..."
Task: "Implement delete_task tool in backend/src/mcp/server.py..."
```

---

## Implementation Strategy

### MVP First (All Phases Required)

Unlike feature-based development, this is a **technical layer integration** where all layers must be complete for MVP:

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T017) - **CRITICAL**
3. Complete Phase 3: MCP Server (T018-T026)
4. Complete Phase 4: Agents (T027-T037)
5. Complete Phase 5: FastAPI Endpoints (T038-T046)
6. **STOP and VALIDATE**: Test chat endpoint with real OpenAI API
7. Complete Phase 6: Testing (T047-T052)
8. Complete Phase 7: Polish (T053-T057)

**Why all layers needed for MVP**: This feature adds a new interface (conversational AI) to existing Phase II functionality. The chat endpoint (Phase 5) requires agents (Phase 4), which require MCP tools (Phase 3), which require conversation persistence (Phase 2). Breaking at any layer results in a non-functional system.

### Incremental Validation Points

Even though all layers are required, validate at phase boundaries:

1. **After Phase 2**: Manually test ConversationService methods work (create conversation, add message, get messages)
2. **After Phase 3**: Manually test MCP server can run standalone (python backend/src/mcp/server.py)
3. **After Phase 4**: Manually test MasterAgent can connect to MCP and process a simple message (mock OpenAI for speed)
4. **After Phase 5**: Test POST /chat with real user message → task created in DB
5. **After Phase 6**: All automated tests pass
6. **After Phase 7**: Performance and stateless design verified

### Execution Timeline Estimate

- **Phase 1 (Setup)**: 15 mins (4 tasks)
- **Phase 2 (Foundational)**: 2-3 hours (13 tasks: models + service)
- **Phase 3 (MCP Server)**: 2-3 hours (9 tasks: infrastructure + 5 tools)
- **Phase 4 (Agents)**: 3-4 hours (11 tasks: 3 sub-agents + Master Agent with 6 methods)
- **Phase 5 (FastAPI)**: 2-3 hours (9 tasks: schemas + 4 endpoints)
- **Phase 6 (Testing)**: 2-3 hours (6 tasks: fixtures + unit + integration)
- **Phase 7 (Polish)**: 1-2 hours (5 tasks: docs + validation)

**Total**: 13-19 hours (57 tasks)

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **File paths** are exact and absolute from repository root
- **No [Story] labels** because this is technical layer integration, not feature stories
- **Phase II unchanged**: Task, User, Auth models and services are reused, not modified
- **Stateless design enforced**: Agent instantiated per request, discarded after response
- **Constitution compliant**: AI-first (natural language interface), MCP-driven (tool-based operations), stateless, sub-agent orchestration, conversation preservation, reusable intelligence
- **Testing strategy**: Unit tests for services/tools/agents, integration tests for end-to-end flow
- **Error handling**: DB → Service → MCP (JSON) → Agent → Natural language
- **Confirmation workflow**: Two-step for destructive operations (delete_task, delete_conversation)
- **Context loading**: Last 20 messages from DB per request (no agent-side caching)
- **MCP-Service contract**: MCP tools MUST call TaskService methods, never raw SQL
- **Performance target**: P95 < 3s per chat request (includes OpenAI latency)

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 13 tasks
- **Phase 3 (MCP Server)**: 9 tasks
- **Phase 4 (Agents)**: 11 tasks
- **Phase 5 (FastAPI)**: 9 tasks
- **Phase 6 (Testing)**: 6 tasks
- **Phase 7 (Polish)**: 5 tasks

**Total**: 57 tasks

**Parallel opportunities**: 20 tasks marked [P] across phases 2, 3, 5, 6, 7
**Critical path**: 37 tasks (linear backbone)

---

## Format Validation ✅

All tasks follow required format:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: Sequential (T001-T057)
- ✅ [P] marker: Present on parallelizable tasks
- ✅ Description: Clear action with exact file path
- ✅ No [Story] labels: Correct for technical layer integration
