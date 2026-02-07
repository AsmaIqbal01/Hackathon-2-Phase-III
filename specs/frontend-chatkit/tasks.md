---
description: "Task list for ChatKit frontend integration implementation"
---

# Tasks: ChatKit Frontend Integration

**Input**: Design documents from `/specs/frontend-chatkit/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

**Tests**: Manual testing checklist (no automated tests required per spec)

**Organization**: Tasks organized by technical layer (setup, API, components, pages, integration) enabling bottom-up frontend development.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/app/`, `frontend/components/`, `frontend/lib/`
- New code isolated in: `frontend/components/chat/`, `frontend/lib/chatApi.ts`

---

## Phase 1: Setup (Dependencies & Environment)

**Purpose**: Install ChatKit, configure environment, verify baseline

- [X] T001 Add @openai/chatkit to frontend/package.json dependencies (Note: Used date-fns instead, custom UI built)
- [X] T002 Run npm install in frontend/ directory to install ChatKit and verify no conflicts
- [X] T003 [P] Create frontend/.env.local with NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 and NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- [X] T004 [P] Verify frontend/.gitignore excludes .env.local
- [X] T005 Verify ChatKit imports work by creating temporary test file, importing ChatKitProvider and ChatView, then deleting test file (Skipped - custom UI implemented)

---

## Phase 2: Foundational (API Client & Types)

**Purpose**: TypeScript interfaces and API client for backend communication

**⚠️ CRITICAL**: API client required by all components

### TypeScript Types

- [X] T006 [P] Create or update frontend/lib/types.ts with ChatMessage interface (id: string, role: 'user' | 'assistant' | 'system', content: string, timestamp: Date)
- [X] T007 [P] Add ChatRequest interface to frontend/lib/types.ts (message: string, conversation_id?: string | null, confirm_action?: object | null)
- [X] T008 [P] Add ChatResponse interface to frontend/lib/types.ts (message: string, conversation_id: string, requires_confirmation: boolean, confirmation_details?: object | null)
- [X] T009 [P] Add ConfirmationDetails interface to frontend/lib/types.ts (action: string, params: Record<string, any>, prompt: string)

### API Client Functions

- [X] T010 Create frontend/lib/chatApi.ts with imports and constants (API_BASE_URL from env, CONVERSATION_ID_KEY for localStorage)
- [X] T011 Implement sendChatMessage function in frontend/lib/chatApi.ts with signature (request: ChatRequest, token: string): Promise<ChatResponse>, POST to /api/chat with Authorization header
- [X] T012 Implement loadConversationHistory function in frontend/lib/chatApi.ts with signature (conversationId: string, token: string): Promise<Message[]>, GET from /api/chat/conversations/{id}/messages
- [X] T013 Implement deleteConversation function in frontend/lib/chatApi.ts with signature (conversationId: string, token: string): Promise<void>, DELETE to /api/chat/conversations/{id}

**Checkpoint**: API client ready - components can communicate with backend

---

## Phase 3: Chat Components

**Purpose**: Build UI components for chat interface

### ChatMessage Component

- [X] T014 Create frontend/components/chat/ChatMessage.tsx with ChatMessageProps interface (role, content, timestamp)
- [X] T015 Implement role-based styling in ChatMessage: user messages right-aligned with bg-gradient-to-r from-neon-blue to-neon-purple, assistant messages left-aligned with bg-cyber-surface border border-cyber-border, system messages centered with text-gray-400 italic text-sm
- [X] T016 Add relative timestamp display in ChatMessage (e.g., "2 min ago") using date-fns or custom formatter

### ConfirmationModal Component

- [X] T017 Create frontend/components/chat/ConfirmationModal.tsx with ConfirmationModalProps interface (isOpen, prompt, action, params, onConfirm, onCancel)
- [X] T018 Implement modal UI in ConfirmationModal: overlay with backdrop-blur, centered dialog box with bg-cyber-surface, prompt text, action details, Confirm button (red/danger) and Cancel button (gray)
- [X] T019 Add modal state management in ConfirmationModal: handle Escape key to close, click outside to cancel, focus trap within modal

### ChatInterface Component

- [X] T020 Create frontend/components/chat/ChatInterface.tsx with state: messages (ChatMessage[]), conversationId (string | null), loading (boolean), error (string | null), confirmationRequest (ConfirmationDetails | null)
- [X] T021 Implement loadHistory method in ChatInterface: read conversation_id from localStorage, call loadConversationHistory if exists, update messages state, handle 404 error (clear localStorage and start new)
- [X] T022 Implement handleSendMessage method in ChatInterface: get token from lib/auth, call sendChatMessage with message and conversation_id, update messages state, save conversation_id to localStorage if new, handle requires_confirmation by setting confirmationRequest state, handle errors by adding system message
- [X] T023 Implement handleConfirmation method in ChatInterface: on Confirm call sendChatMessage with confirm_action parameter and display result, on Cancel add "Action cancelled" system message and close modal
- [X] T024 Implement startNewConversation method in ChatInterface: clear messages array, set conversationId to null, remove from localStorage using CONVERSATION_ID_KEY
- [X] T025 Integrate ChatKit into ChatInterface: wrap with ChatKitProvider using domainKey from env, add ChatView component with messages prop, onSend prop (handleSendMessage), isLoading prop (loading state), placeholder prop, theme config matching Phase II (dark mode with neon colors) (Custom UI implemented instead)
- [X] T026 Add auto-scroll behavior in ChatInterface: useEffect with messages dependency to scroll to bottom on new message, use smooth scroll behavior
- [X] T027 Add useEffect in ChatInterface to load conversation history on mount by calling loadHistory()

**Checkpoint**: Chat components functional - ready for page integration

---

## Phase 4: Pages & Navigation

**Purpose**: Create chat page and integrate with existing navigation

- [X] T028 Create frontend/app/chat/page.tsx with 'use client' directive, auth check using isAuthenticated (redirect to /login if false), page layout with header containing "AI Task Assistant" title and New Chat button and Logout button
- [X] T029 Import and render ChatInterface component in frontend/app/chat/page.tsx, pass startNewConversation callback to New Chat button, add BlobBackground component if available from Phase II
- [X] T030 Add AI Chat navigation link in frontend/app/dashboard/page.tsx: add button or link with href="/chat" using NeonButton component if available, keep existing Phase II task UI for backward compatibility

**Checkpoint**: Chat page accessible via /chat route and dashboard navigation

---

## Phase 5: Integration & Error Handling

**Purpose**: Polish error states, loading indicators, and edge cases

**Note**: Core error handling, loading states, and localStorage persistence are implemented in ChatInterface (T020-T027). Additional polish tasks below can be completed post-deployment.

### Error Handling

- [X] T031 Implement comprehensive error handling in ChatInterface: catch network errors and display as system message with red text and retry button, handle 401 by calling clearToken and redirecting to /login, handle 403/404/500 with appropriate error messages (Implemented in ChatInterface.handleSendMessage)
- [X] T032 Add error recovery in ChatInterface: retry button calls handleSendMessage with last message, preserve user message in input on error (don't clear), show error details in system message (Implemented with lastMessageRef and handleRetry)

### Loading & UX Polish

- [X] T033 Implement loading states in ChatInterface: set loading=true before API call, disable input during loading, show "AI is thinking..." system message or use ChatKit isLoading prop, clear loading after response (Implemented with animated dots indicator)
- [X] T034 Add message timestamp formatting: install date-fns or use Intl.RelativeTimeFormat for "2 min ago" style timestamps, display below each message (Implemented in ChatMessage with date-fns)
- [ ] T035 Test mobile responsive layout: verify messages stack properly on small screens (< 640px), verify input box accessible, verify buttons clickable, adjust ChatInterface styling if needed (Manual testing required)

### localStorage Persistence

- [ ] T036 Test conversation persistence: verify conversation_id saves to localStorage after first message, verify conversation_id loads on page mount, verify messages persist across page refreshes, verify New Chat clears localStorage (Manual testing required)

**Checkpoint**: All features functional with error handling and polish

---

## Phase 6: Validation & Documentation

**Purpose**: Final validation and documentation updates

**Note**: Documentation and manual testing tasks to be completed post-implementation review.

- [ ] T037 Update frontend/README.md or root README with /chat route documentation, environment variables (NEXT_PUBLIC_OPENAI_DOMAIN_KEY, NEXT_PUBLIC_API_BASE_URL), ChatKit setup instructions, usage examples (send message, new chat, delete conversation)
- [ ] T038 Final validation checklist: verify ChatKit renders messages correctly, verify messages send to backend and display responses, verify conversation persists across refreshes, verify confirmation modal appears for delete operations, verify errors display as system messages, verify auth integration works (401 redirect), verify New Chat clears conversation, verify mobile responsive, verify no console errors, verify Phase II dashboard still accessible

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T005) - BLOCKS Phase 3
- **Components (Phase 3)**: Depends on Foundational completion (T013) - Types and API client must exist
- **Pages (Phase 4)**: Depends on Components completion (T027) - ChatInterface must be functional
- **Integration (Phase 5)**: Depends on Pages completion (T030) - Full page must exist to test
- **Validation (Phase 6)**: Depends on Integration completion (T036) - All features must work

### Critical Path

```
T001 → T002 → T005 → T010 → T011 → T020 → T022 → T025 → T027 → T028 → T029 → T031 → T036 → T038
```

**Linear backbone**: Setup → API Client → ChatInterface → Chat Page → Error Handling → Validation

### Within Each Phase

**Phase 1 (Setup)**:
- T003-T004 can run in parallel [P] after T002

**Phase 2 (Foundational)**:
- T006-T009 (types) can run in parallel [P] after T005
- T011-T013 (API functions) run sequentially after T010

**Phase 3 (Components)**:
- T014-T016 (ChatMessage) run sequentially
- T017-T019 (ConfirmationModal) run sequentially after T016
- T020-T027 (ChatInterface) run sequentially (each method builds on previous)

**Phase 4 (Pages)**:
- T028-T029 run sequentially
- T030 can run in parallel [P] after T027 (different file)

**Phase 5 (Integration)**:
- T031-T032 run sequentially (error handling)
- T033-T035 run sequentially (loading & UX)
- T036 is verification task

**Phase 6 (Validation)**:
- T037-T038 run sequentially

### Parallel Opportunities

```bash
# Phase 1: Environment setup
T003 (.env.local) + T004 (.gitignore check)

# Phase 2: Type definitions
T006 (ChatMessage) + T007 (ChatRequest) + T008 (ChatResponse) + T009 (ConfirmationDetails)

# Phase 4: Navigation
T030 (dashboard link) - can run parallel with T028-T029 (different file)
```

---

## Parallel Example: Phase 2 (Types)

```bash
# After T005 (imports verified), launch all type definitions together:
Task: "Create ChatMessage interface in frontend/lib/types.ts"
Task: "Add ChatRequest interface to frontend/lib/types.ts"
Task: "Add ChatResponse interface to frontend/lib/types.ts"
Task: "Add ConfirmationDetails interface to frontend/lib/types.ts"
```

---

## Implementation Strategy

### MVP First (All Phases Required)

Unlike feature-based development, this is a **frontend layer integration** where all components must be complete for MVP:

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013)
3. Complete Phase 3: Components (T014-T027)
4. Complete Phase 4: Pages (T028-T030)
5. **STOP and VALIDATE**: Manually test /chat page with backend
6. Complete Phase 5: Integration (T031-T036)
7. Complete Phase 6: Validation (T037-T038)

**Why all layers needed for MVP**: Chat page requires ChatInterface, which requires ChatMessage and ConfirmationModal, which require API client, which requires types and ChatKit. Breaking at any layer results in non-functional UI.

### Incremental Validation Points

Even though all layers are required, validate at phase boundaries:

1. **After Phase 1**: Verify npm install succeeds, ChatKit imports work
2. **After Phase 2**: Test API client can communicate with backend (use browser console or temporary test)
3. **After Phase 3**: Verify ChatInterface component renders without errors
4. **After Phase 4**: Test /chat page loads and displays chat interface
5. **After Phase 5**: Test all features (send, receive, errors, confirmation)
6. **After Phase 6**: Documentation complete, all validation passed

### Execution Timeline Estimate

- **Phase 1 (Setup)**: 15 mins (5 tasks)
- **Phase 2 (Foundational)**: 1 hour (8 tasks: types + API client)
- **Phase 3 (Components)**: 3 hours (14 tasks: 3 components with full implementation)
- **Phase 4 (Pages)**: 30 mins (3 tasks: page + navigation)
- **Phase 5 (Integration)**: 1.5 hours (6 tasks: errors, loading, testing)
- **Phase 6 (Validation)**: 30 mins (2 tasks: docs + validation)

**Total**: 7-8 hours (38 tasks)

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **File paths** are exact and absolute from repository root
- **No [Story] labels** because this is technical layer integration, not feature stories
- **Phase II unchanged**: Auth, API client, Tailwind theme reused
- **Stateless design**: Only conversation_id in localStorage, all messages in backend DB
- **ChatKit integration**: Attempt official library, fallback to custom UI if unavailable
- **Error handling**: System messages + retry button
- **Confirmation workflow**: Modal dialog for destructive operations
- **Mobile responsive**: Tailwind responsive classes
- **Backward compatible**: Phase II dashboard kept functional

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (Components)**: 14 tasks
- **Phase 4 (Pages)**: 3 tasks
- **Phase 5 (Integration)**: 6 tasks
- **Phase 6 (Validation)**: 2 tasks

**Total**: 38 tasks

**Parallel opportunities**: 7 tasks marked [P] across phases 1, 2, 4
**Critical path**: 31 tasks (linear backbone)

---

## Format Validation ✅

All tasks follow required format:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: Sequential (T001-T038)
- ✅ [P] marker: Present on parallelizable tasks
- ✅ Description: Clear action with exact file path
- ✅ No [Story] labels: Correct for technical layer integration

---

## Manual Testing Checklist (Phase 5-6)

**Basic Flow** (T036):
- [ ] User can send message and receive response
- [ ] conversation_id persists in localStorage
- [ ] Messages persist across page refresh
- [ ] New Chat clears conversation and starts fresh

**Task Operations via Chat** (T036):
- [ ] "Create a task called X" → Backend creates task, assistant confirms
- [ ] "List my tasks" → Backend returns tasks, assistant displays in message
- [ ] "Mark task X as complete" → Backend updates task, assistant confirms
- [ ] "Delete task X" → Confirmation modal appears → Confirm → Task deleted

**Error Handling** (T031-T032):
- [ ] Network error → Error message displayed with retry button
- [ ] 401 error → Token cleared, redirected to /login
- [ ] 500 error → Error message displayed
- [ ] Invalid request → Error message from backend displayed

**Confirmation Workflow** (T023):
- [ ] Delete request triggers confirmation modal
- [ ] Modal shows action details
- [ ] Cancel → Modal closes, "Action cancelled" message
- [ ] Confirm → Action executes, result displayed

**Mobile Responsive** (T035):
- [ ] Messages readable on small screens
- [ ] Input box accessible
- [ ] Buttons clickable
- [ ] Layout adapts to viewport

**Authentication** (T031):
- [ ] Unauthenticated user redirected to /login
- [ ] JWT token included in all requests
- [ ] 401 during chat session redirects to login

**Backward Compatibility** (T038):
- [ ] Phase II dashboard still accessible
- [ ] Dashboard link to /chat works
- [ ] Phase II task CRUD UI still functional (if desired)

---

## Implementation Notes

**ChatKit Fallback**:
- If @openai/chatkit package doesn't exist or is incompatible:
  - Build custom chat UI with React components
  - Use existing Phase II styling patterns
  - Focus on functionality over branding
  - Update tasks T001, T002, T005, T025 accordingly

**Phase II Reuse**:
- Auth utilities: Import from lib/auth.ts (getToken, isAuthenticated, clearToken)
- API pattern: Reference lib/api.ts for fetch wrapper pattern
- UI components: Use NeonButton, BlobBackground if available
- Tailwind: Apply existing theme classes (neon-blue, cyber-surface, etc.)

**State Management**:
- Use React useState (no Redux, Zustand, or context)
- Simple prop drilling (only 3 components)
- localStorage for conversation_id only

**Error Strategy**:
- All errors displayed as system messages (red text)
- Retry button for recoverable errors
- Auto-redirect for auth errors
- Graceful degradation for API failures

**Performance**:
- No optimization needed (simple React app)
- ChatKit handles message virtualization
- Lazy load conversation history (only on mount if conversation_id exists)

**Security**:
- JWT token in Authorization header (never localStorage)
- Only conversation_id in localStorage (not sensitive)
- React auto-escapes content (XSS protection)
- CORS configured in backend

---

## Suggested MVP Scope

**Minimum Viable Product** (for first deployment):
- ✅ Phases 1-4 (Setup + API + Components + Pages)
- ✅ Basic error handling (display errors, no retry button initially)
- ✅ Confirmation workflow
- ⏭️ Skip: Advanced error recovery (T032), timestamp formatting (T034), mobile testing (T035)

**Post-MVP Enhancements**:
- Phase 5 polish (error recovery, loading polish, mobile optimization)
- Phase 6 documentation
- Tool transparency (optional FR8 from spec)
- Conversation list sidebar (out of scope for Phase III, future enhancement)
