---
id: 002
title: Task generation for backend AI MCP integration
stage: tasks
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: backend-ai-mcp
branch: main
user: system
command: /sp.tasks
labels: ["tasks", "task-generation", "implementation", "backend-ai-mcp"]
links:
  spec: specs/backend-ai-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/backend-ai-mcp/tasks.md
tests:
 - (tests defined in Phase 6 of tasks.md)
---

## Prompt

/sp.tasks

(No additional user input provided - executed directly after /sp.plan)

## Response snapshot

Generated comprehensive task list with 57 tasks across 7 phases for backend AI + MCP integration:

**Phase 1: Setup (4 tasks)**
- Add dependencies (openai>=1.0.0, mcp>=1.0.0) to requirements.txt
- Configure OPENAI_API_KEY environment variable
- Install dependencies and verify no conflicts
- Run Phase II baseline tests to ensure no regressions

**Phase 2: Foundational (13 tasks) - BLOCKING**
- Create Conversation and Message database models
- Update models __init__.py and database.py imports
- Run database migration (Alembic or create_all)
- Add ConversationNotFoundError to utils/errors.py
- Implement ConversationService with 6 methods:
  - create_conversation, get_conversation, list_conversations
  - add_message, get_messages, delete_conversation
- All methods enforce user ownership (same pattern as TaskService)

**Phase 3: MCP Server Layer (9 tasks)**
- Create MCP module structure (mcp/__init__.py, context.py)
- Initialize MCP Server with stdio_server
- Implement 5 MCP tools delegating to TaskService:
  - add_task, list_tasks, complete_task, update_task, delete_task
- Each tool returns structured JSON: {success, data/error, message}
- Complete main() function with asyncio entry point

**Phase 4: OpenAI Agents Layer (11 tasks)**
- Create agents module structure (agents/__init__.py)
- Implement 3 sub-agents:
  - ConfirmationSubAgent (check_required, request_confirmation, execute_confirmed)
  - TaskSubAgent (handle with intent-to-tool mapping)
  - ConversationSubAgent (handle for history queries)
- Implement MasterAgent with 6 methods:
  - __init__ (instantiate sub-agents)
  - connect_mcp() (stdio client to MCP server)
  - _load_history() (last 20 messages from DB)
  - _format_mcp_tools() (convert to OpenAI format)
  - _execute_tools() (call MCP tools, handle confirmations)
  - _check_confirmation_needed() (check for required confirmations)
  - process_message() (main orchestration with OpenAI API)

**Phase 5: FastAPI Chat Endpoints (9 tasks)**
- Create chat schemas (ChatRequest, ChatResponse, ConversationResponse, MessageResponse)
- Create chat router with /chat prefix
- Implement POST /chat with 3 parts:
  - Confirmation handling (execute_confirmed)
  - Normal message processing (agent.process_message)
  - Persistence (save user + assistant messages via ConversationService)
- Implement conversation management endpoints:
  - GET /conversations (list user's conversations)
  - GET /conversations/{id}/messages (get history)
  - DELETE /conversations/{id} (delete conversation)
- Register chat router in main.py

**Phase 6: Testing (6 tasks)**
- Create conversation fixtures (test_conversation, test_message, etc.)
- Write ConversationService unit tests (7 test cases)
- Write MCP tool unit tests (5 tools + error handling)
- Write Master Agent unit tests (mock OpenAI + MCP)
- Write end-to-end integration tests (4 scenarios)
- Run full test suite with coverage verification

**Phase 7: Polish & Cross-Cutting Concerns (5 tasks)**
- Update README/API docs with chat endpoints
- Verify stateless design (restart test)
- Verify Phase II baseline unchanged
- Performance baseline (P95 < 3s target)
- Final validation checklist (8 items)

**Task Organization**:
- **Format**: `- [ ] T### [P?] Description with file path`
- **[P] marker**: 20 tasks marked for parallel execution
- **Critical path**: 37 sequential tasks (linear backbone)
- **Dependencies**: Clear phase boundaries with validation checkpoints

**Parallel Opportunities**:
- Phase 2: Database models (T005-T006), Service methods (T012-T014)
- Phase 3: All 5 MCP tools (T021-T025)
- Phase 5: Conversation endpoints (T043-T045)
- Phase 6: All unit tests (T048-T050)
- Phase 7: Docs and validation (T053-T056)

**Implementation Strategy**:
- **MVP = All Phases**: Technical layer integration requires complete stack
- **Validation points**: Test at phase boundaries (after Foundational, MCP, Agents, API, Testing)
- **Estimated timeline**: 13-19 hours total
- **Phase II unchanged**: Task/User/Auth models reused, not modified

**Key Architectural Constraints**:
- Stateless design: Agent per request, DB-loaded context
- MCP-Service contract: Tools MUST call TaskService, never raw SQL
- Confirmation workflow: Two-step for delete operations
- Context strategy: Last 20 messages from DB (no agent caching)
- Error propagation: DB → Service → MCP (JSON) → Agent → Natural language
- Performance target: P95 < 3s including OpenAI latency

**Format Validation**:
✅ All 57 tasks follow checklist format
✅ Sequential IDs (T001-T057)
✅ [P] markers on parallelizable tasks
✅ Exact file paths in descriptions
✅ No [Story] labels (technical layer integration, not feature stories)

## Outcome

- ✅ Impact: 57 executable tasks generated with clear dependencies and parallel opportunities
- 🧪 Tests: Testing phase (Phase 6) with 6 tasks covering fixtures, unit, and integration tests
- 📁 Files: Created specs/backend-ai-mcp/tasks.md (336 lines)
- 🔁 Next prompts: Run /sp.implement to execute tasks programmatically, or manually execute tasks in order (T001→T002→...→T057)
- 🧠 Reflection: Task organization follows architectural layers (Setup → Foundation → MCP → Agents → API → Tests → Polish) rather than feature stories, which is appropriate for technical infrastructure integration. All phases required for MVP since chat endpoint depends on full stack.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation successful with proper format validation
- Graders run and results (PASS/FAIL): Format validation: PASS (all 57 tasks follow checklist format with checkboxes, IDs, [P] markers, and file paths)
- Prompt variant (if applicable): Standard /sp.tasks workflow following plan.md structure
- Next experiment (smallest change to try): Execute Phase 1 (Setup) tasks to install dependencies and verify baseline
