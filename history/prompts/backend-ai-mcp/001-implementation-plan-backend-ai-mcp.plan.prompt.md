---
id: 001
title: Implementation plan for backend AI + MCP integration
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: backend-ai-mcp
branch: main
user: system
command: /sp.plan
labels: ["planning", "architecture", "mcp", "openai-agents", "phase-iii"]
links:
  spec: specs/backend-ai-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/backend-ai-mcp/plan.md
 - specs/backend-ai-mcp/spec.md (moved from specs/spec-A-backend-ai-mcp.md)
tests:
 - (none - planning phase)
---

## Prompt

/sp.plan

Input Spec:
- /specs/spec-A-backend-mcp-agents.md

Context:
- This is Phase III of an existing project.
- Phase II backend code already exists and must be reused as reusable intelligence.
- Goal is to upgrade Phase II backend into a stateless AI-driven backend using:
  - FastAPI
  - OpenAI Agents SDK
  - Official MCP SDK
- Server must remain stateless; all state lives in the database.

Planning Rules:
1. Produce a minimal, ordered execution plan.
2. Break work into small, testable tasks.
3. Each task must include:
   - Task name
   - Purpose
   - Files or modules affected
   - Dependencies
4. Tasks must follow correct dependency order.
5. Avoid redesigning or duplicating Phase II logic.
6. Do NOT include frontend, deployment, or auth UI tasks.
7. Avoid extra abstractions or speculative features.
8. Plan must be directly executable via `/sp.implement`.

Required Task Categories (in order):
1. Phase II model verification & alignment
2. MCP server setup
3. MCP tool implementations:
   - add_task
   - list_tasks
   - complete_task
   - update_task
   - delete_task
4. OpenAI Agents SDK integration:
   - Master Agent
   - Task Sub-Agent
   - Conversation Sub-Agent
   - Confirmation Sub-Agent
5. FastAPI chat endpoint
6. Conversation management endpoints
7. Testing (unit + integration)

## Response snapshot

Created comprehensive implementation plan with 54 tasks across 7 phases:

**Phase 0: Preparation & Dependencies** (3 tasks)
- Update requirements.txt with openai>=1.0.0 and mcp>=1.0.0
- Add OPENAI_API_KEY to environment variables
- Verify Phase II baseline (run existing tests)

**Phase 1: Database Models & Schema** (5 tasks)
- Create Conversation model (id, user_id, title, timestamps)
- Create Message model (id, conversation_id, role, content, metadata, created_at)
- Update models __init__.py to export new models
- Update database.py imports
- Run database migration (Alembic or create_all)

**Phase 2: ConversationService** (8 tasks)
- Create service class following TaskService pattern
- Implement create_conversation, get_conversation, list_conversations
- Implement add_message, get_messages
- Implement delete_conversation with cascade
- Add ConversationNotFoundError to utils/errors.py
- Enforce user ownership (same security pattern as TaskService)

**Phase 3: MCP Server & Tools** (8 tasks)
- Create MCP context manager (get_context_user_id, get_db_session)
- Initialize MCP server with stdio_server
- Implement 5 MCP tools delegating to TaskService:
  - add_task (create task)
  - list_tasks (query with filters)
  - complete_task (update status)
  - update_task (partial update)
  - delete_task (requires confirmation)
- Complete main() function with asyncio

**Phase 4: OpenAI Agents SDK Integration** (10 tasks)
- Create 3 sub-agents:
  - ConfirmationSubAgent (check_required, request_confirmation, execute_confirmed)
  - TaskSubAgent (handle intent routing to MCP tools)
  - ConversationSubAgent (handle history queries)
- Create MasterAgent with 6 methods:
  - __init__ (instantiate sub-agents)
  - connect_mcp() (stdio client to MCP server)
  - _load_history() (load last 20 messages from DB)
  - _format_mcp_tools() (convert to OpenAI function format)
  - _execute_tools() (call MCP tools, handle confirmations)
  - _check_confirmation_needed() (check if confirmation required)
  - process_message() (main orchestration with OpenAI API)

**Phase 5: FastAPI Chat Endpoints** (9 tasks)
- Create chat schemas (ChatRequest, ChatResponse, ConversationResponse, MessageResponse)
- Create chat router with /chat prefix
- Implement POST /chat with 3 parts:
  - Confirmation handling (execute_confirmed)
  - Normal message processing (agent.process_message)
  - Persistence (save user + assistant messages to DB)
- Implement GET /conversations (list user's conversations)
- Implement GET /conversations/{id}/messages (get conversation history)
- Implement DELETE /conversations/{id} (delete conversation + messages)
- Register chat router in main.py

**Phase 6: Testing** (6 tasks)
- Create conversation fixtures (test_conversation, test_message, etc.)
- Write ConversationService unit tests (7 test cases)
- Write MCP tool unit tests (5 tools + error handling)
- Write Master Agent unit tests (mocking OpenAI + MCP)
- Write end-to-end integration test (user → agent → MCP → DB → response)
- Run full test suite, verify 100% coverage for new code, no Phase II regressions

**Phase 7: Documentation & Cleanup** (5 tasks)
- Update README/API docs with /chat endpoints
- Verify stateless design (restart server mid-conversation)
- Verify Phase II baseline unchanged (frontend still works)
- Performance baseline (P95 < 3s target)
- Final validation checklist (constitution compliance)

**Key Design Decisions**:
- Stateless: Agent instantiated per request, discarded after response
- Context loading: Last 20 messages loaded from DB each request
- Confirmation workflow: Two-step for delete_task (agent detects, user confirms, agent executes)
- Error propagation: DB → Service → MCP (JSON) → Agent → Natural language
- Reuse strategy: TaskService unchanged, new ConversationService follows same pattern
- MCP-Service integration: MCP tools call TaskService methods, never raw SQL

**Dependency Graph**:
- Linear critical path: Prep → Models → Services → MCP → Agents → API → Tests
- Parallelizable: MCP tools (19-23), Unit tests (45-47)
- 54 total tasks with clear dependencies documented

**Constitution Compliance**:
✅ AI-First Architecture (natural language interface)
✅ MCP-Driven Operations (all task ops via MCP tools)
✅ Stateless Design (no agent state persists)
✅ Sub-Agent Orchestration (Master → Task/Conversation/Confirmation)
✅ Conversation Context Preservation (DB-backed messages)
✅ Reusable Intelligence (Phase II unchanged)

## Outcome

- ✅ Impact: Comprehensive plan created with 54 tasks, ready for /sp.tasks execution
- 🧪 Tests: Testing strategy defined (Phase 6: unit + integration tests)
- 📁 Files: Created specs/backend-ai-mcp/plan.md, reorganized spec into feature directory
- 🔁 Next prompts: Run /sp.tasks to generate detailed tasks.md, then /sp.implement to execute
- 🧠 Reflection: Plan follows SDD structure, maintains strict separation between Phase II (unchanged) and Phase III (additive), enforces constitution principles

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation successful
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Execute /sp.tasks to generate actionable task list
