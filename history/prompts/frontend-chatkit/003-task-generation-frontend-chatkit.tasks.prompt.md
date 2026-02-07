---
id: 003
title: Task generation for ChatKit frontend integration
stage: tasks
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: frontend-chatkit
branch: main
user: system
command: /sp.tasks
labels: ["tasks", "frontend", "chatkit", "nextjs", "task-generation"]
links:
  spec: specs/frontend-chatkit/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/frontend-chatkit/tasks.md
tests:
 - (manual testing checklist defined in tasks.md)
---

## Prompt

/sp.tasks

(No additional user input - executed directly after /sp.plan for Spec B)

## Response snapshot

Generated comprehensive task list with 38 tasks across 6 phases for ChatKit frontend integration:

**Phase 1: Setup (5 tasks)**
- T001: Add @openai/chatkit to package.json
- T002: Run npm install and verify no conflicts
- T003 [P]: Create .env.local with API_BASE_URL and OPENAI_DOMAIN_KEY
- T004 [P]: Verify .gitignore excludes .env.local
- T005: Verify ChatKit imports work (test import and delete)

**Phase 2: Foundational (8 tasks) - BLOCKING**
- T006-T009 [P]: Create TypeScript interfaces:
  - ChatMessage (id, role, content, timestamp)
  - ChatRequest (message, conversation_id, confirm_action)
  - ChatResponse (message, conversation_id, requires_confirmation, confirmation_details)
  - ConfirmationDetails (action, params, prompt)
- T010-T013: Implement API client functions:
  - T010: Create chatApi.ts with constants
  - T011: sendChatMessage function (POST /api/chat)
  - T012: loadConversationHistory function (GET /messages)
  - T013: deleteConversation function (DELETE /conversations/{id})

**Phase 3: Components (14 tasks)**
*ChatMessage Component (T014-T016)*:
- Create component with props interface
- Implement role-based styling (user: right/blue, assistant: left/dark, system: center/gray)
- Add relative timestamp display

*ConfirmationModal Component (T017-T019)*:
- Create component with props interface
- Implement modal UI (overlay, dialog, buttons)
- Add modal state management (Escape key, click outside, focus trap)

*ChatInterface Component (T020-T027)*:
- T020: Create with state (messages, conversationId, loading, error, confirmationRequest)
- T021: Implement loadHistory method (load from localStorage + backend)
- T022: Implement handleSendMessage method (send to backend, update state, save conversation_id)
- T023: Implement handleConfirmation method (confirm/cancel workflow)
- T024: Implement startNewConversation method (clear state and localStorage)
- T025: Integrate ChatKit (ChatKitProvider, ChatView with props and theming)
- T026: Add auto-scroll behavior (useEffect on messages)
- T027: Add loadHistory useEffect on mount

**Phase 4: Pages & Navigation (3 tasks)**
- T028: Create /chat page with auth check and layout
- T029: Import ChatInterface, wire up New Chat and Logout buttons
- T030 [P]: Add "AI Chat" link to dashboard navigation

**Phase 5: Integration & Polish (6 tasks)**
- T031-T032: Error handling (catch errors, display system messages, retry button, 401 redirect)
- T033: Loading states (disable input, show "thinking" indicator)
- T034: Timestamp formatting (date-fns or Intl.RelativeTimeFormat)
- T035: Test mobile responsive layout
- T036: Test localStorage persistence (save, load, clear)

**Phase 6: Validation & Documentation (2 tasks)**
- T037: Update README with /chat documentation, env vars, usage examples
- T038: Final validation checklist (10 criteria)

**Task Organization**:
- Format: `- [ ] T### [P?] Description with file path`
- 7 tasks marked [P] for parallel execution
- Critical path: 31 sequential tasks
- Clear phase boundaries with validation checkpoints

**Parallel Opportunities**:
- Phase 1: T003+T004 (env setup + gitignore check)
- Phase 2: T006+T007+T008+T009 (all type definitions)
- Phase 4: T030 (dashboard link, different file from chat page)

**Implementation Strategy**:
- Bottom-up: Types → API → Components → Page
- Sequential component development: ChatMessage → Modal → Interface
- Validation at phase boundaries
- MVP = All phases (chat page requires full stack)

**Manual Testing Checklist**:
- Basic flow (send/receive/persist/new chat)
- Task operations (create/list/complete/delete via chat)
- Error handling (network/401/500 errors)
- Confirmation workflow (modal display, confirm/cancel)
- Mobile responsive
- Auth integration (401 redirect)
- Backward compatibility (Phase II dashboard)

**ChatKit Fallback**:
- Primary: Use @openai/chatkit package
- Fallback: Build custom React chat UI if package unavailable
- Tasks T001, T002, T005, T025 would need adjustment

**Key Technical Decisions**:
- localStorage: Only conversation_id (40 bytes, stateless design)
- State management: React useState (no Redux)
- API client: Separate chatApi.ts (clean separation)
- Styling: Reuse Phase II Tailwind theme
- Error display: System messages + retry button
- Confirmation: Modal dialog (clear UX)

**Phase II Reuse**:
- Auth utilities: lib/auth.ts (getToken, isAuthenticated, clearToken)
- API client pattern: lib/api.ts (reference for fetch wrapper)
- UI components: NeonButton, BlobBackground (if available)
- Tailwind theme: neon-blue, neon-purple, cyber-dark, cyber-surface

**Timeline**: 7-8 hours (38 tasks) with validation checkpoints

**Dependencies**:
- Spec A backend ✅ (implemented and deployed)
- Phase II auth ✅ (existing)
- Phase II Tailwind ✅ (existing)
- ChatKit package (to be installed in T001)

**Constitution Compliance**:
✅ AI-First (chat primary interface)
✅ Stateless (only conversation_id persisted)
✅ Reusable Intelligence (Phase II auth/styles reused)
✅ Conversation Preservation (localStorage + backend DB)

## Outcome

- ✅ Impact: 38 executable tasks generated with clear dependencies and validation points
- 🧪 Tests: Manual testing checklist with 7 categories (30+ test cases)
- 📁 Files: Created specs/frontend-chatkit/tasks.md (386 lines)
- 🔁 Next prompts: Run /sp.implement to execute tasks programmatically, or manually execute T001→T002→...→T038
- 🧠 Reflection: Task organization follows architectural layers (Setup → API → Components → Pages → Integration → Validation). All phases required for MVP since chat page depends on full component stack. Clear fallback strategy if ChatKit unavailable.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation successful with proper format validation
- Graders run and results (PASS/FAIL): Format validation: PASS (all 38 tasks follow checklist format with checkboxes, IDs, [P] markers, and file paths)
- Prompt variant (if applicable): Standard /sp.tasks workflow following plan.md structure
- Next experiment (smallest change to try): Execute Phase 1 (Setup) to install ChatKit and verify imports work
