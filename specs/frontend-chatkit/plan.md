# Implementation Plan: ChatKit Frontend Integration

**Branch**: `main` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/frontend-chatkit/spec.md`

## Summary

Build minimal conversational UI using OpenAI ChatKit for natural language task management. Frontend is pure display layer with no business logic, connecting to Phase III backend /api/chat endpoint. Reuses Phase II auth utilities and Tailwind theme. Provides both chat and traditional dashboard for backward compatibility.

## Technical Context

**Language/Version**: TypeScript 5.9+, React 19.2+
**Primary Dependencies**: Next.js 16.1+ (App Router), OpenAI ChatKit 1.0+, Tailwind CSS 4.1+
**Storage**: localStorage (conversation_id only), Backend PostgreSQL (messages)
**Testing**: Manual testing checklist (no automated tests required)
**Target Platform**: Web (Vercel deployment)
**Project Type**: Web frontend (Next.js App Router)
**Performance Goals**: Page load < 1s, message send < 500ms, history load < 2s
**Constraints**: No business logic, no task CRUD UI, chat-only interface, minimal styling
**Scale/Scope**: Single-user chat sessions, 20-message context window, 3 main components

## Constitution Check

✅ **AI-First Architecture**: Chat interface is primary task management mode
✅ **Stateless Design**: Frontend stores only conversation_id, all state in backend DB
✅ **Reusable Intelligence**: Phase II auth/API utilities reused unchanged
✅ **Conversation Context Preservation**: conversation_id persistence enables continuity
✅ **Technology Stack Compliance**: OpenAI ChatKit + Next.js + Vercel deployment

**Violations**: None

**Note**: Frontend-specific principles (MCP-Driven, Sub-Agent Orchestration) apply to backend only.

## Project Structure

### Documentation (this feature)

```text
specs/frontend-chatkit/
├── spec.md              # Feature specification
└── plan.md              # This file
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx           # [NEW] Chat page
│   ├── dashboard/
│   │   └── page.tsx           # [MODIFIED] Add chat link
│   ├── layout.tsx             # [REUSED] Phase II
│   ├── globals.css            # [REUSED] Phase II
│   └── page.tsx               # [REUSED] Phase II landing
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx  # [NEW] Main chat orchestrator
│   │   ├── ChatMessage.tsx    # [NEW] Message display
│   │   └── ConfirmationModal.tsx # [NEW] Confirmation dialog
│   ├── TaskList.tsx           # [REUSED] Phase II (backward compat)
│   ├── TaskForm.tsx           # [REUSED] Phase II (backward compat)
│   └── ui/                    # [REUSED] Phase II components
├── lib/
│   ├── chatApi.ts             # [NEW] Chat API client
│   ├── api.ts                 # [REUSED] Phase II
│   ├── auth.ts                # [REUSED] Phase II
│   └── types.ts               # [MODIFIED] Add chat types
├── .env.local                 # [MODIFIED] Add OPENAI_DOMAIN_KEY
└── package.json               # [MODIFIED] Add @openai/chatkit
```

**Structure Decision**: Next.js App Router (existing). New code isolated in `app/chat/` and `components/chat/`. Phase II components kept for backward compatibility.

## Complexity Tracking

No constitution violations. Complexity justified by requirements:
- **3 chat components**: Minimal for chat UI (interface, message, modal)
- **ChatKit dependency**: Required by constitution for OpenAI integration
- **localStorage usage**: Required for stateless frontend (conversation continuity)

---

## Implementation Phases

### Phase 0: Preparation & Research

**Goal**: Verify ChatKit API, configure environment, understand integration patterns

**Research Tasks**:

1. **Verify ChatKit package and API**
   - Check if `@openai/chatkit` exists on npm
   - Review ChatKit documentation for React/Next.js integration
   - Identify: ChatKitProvider, ChatView components and their props
   - Identify: Message format requirements
   - **Output**: Research findings for ChatKit integration patterns

2. **Review Phase II frontend structure**
   - Examine existing Next.js App Router setup
   - Review auth utilities (lib/auth.ts)
   - Review API client (lib/api.ts)
   - Review Tailwind configuration and theme
   - **Output**: Understanding of reusable components and patterns

3. **Define TypeScript interfaces**
   - ChatMessage interface (id, role, content, timestamp)
   - ChatRequest interface (message, conversation_id, confirm_action)
   - ChatResponse interface (message, conversation_id, requires_confirmation, confirmation_details)
   - **Output**: Type definitions for API integration

**Checkpoint**: Research complete, ChatKit integration patterns understood

---

### Phase 1: Setup & Dependencies

**Goal**: Install ChatKit, configure environment, verify imports

**Tasks**:

4. **Install ChatKit dependency**
   - Add `@openai/chatkit` to frontend/package.json dependencies
   - Run `npm install` in frontend directory
   - Verify package installs without conflicts
   - **Files**: `frontend/package.json`, `frontend/package-lock.json`
   - **Dependencies**: Task 1

5. **Configure environment variables**
   - Create/update `frontend/.env.local`
   - Add `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
   - Add `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key-here`
   - Add `.env.local` to `.gitignore` if not present
   - **Files**: `frontend/.env.local`, `frontend/.gitignore`
   - **Dependencies**: None

6. **Verify ChatKit imports**
   - Create test file to verify imports work
   - Test: `import { ChatKitProvider, ChatView } from '@openai/chatkit'`
   - Delete test file after verification
   - **Files**: None (verification only)
   - **Dependencies**: Task 4

**Checkpoint**: Dependencies installed, environment configured

---

### Phase 2: API Client Layer

**Goal**: Implement TypeScript API client for backend chat endpoints

**Tasks**:

7. **Create chat API types**
   - File: `frontend/lib/types.ts` or update existing types file
   - Add ChatMessage interface
   - Add ChatRequest interface
   - Add ChatResponse interface
   - Add ConfirmationDetails interface
   - **Files**: `frontend/lib/types.ts`
   - **Dependencies**: Task 3

8. **Implement sendChatMessage function**
   - File: `frontend/lib/chatApi.ts`
   - Function: `sendChatMessage(request: ChatRequest, token: string): Promise<ChatResponse>`
   - POST to `${NEXT_PUBLIC_API_BASE_URL}/api/chat`
   - Include Authorization header with JWT
   - Parse response and handle errors
   - **Files**: `frontend/lib/chatApi.ts`
   - **Dependencies**: Task 7

9. **Implement loadConversationHistory function**
   - File: `frontend/lib/chatApi.ts`
   - Function: `loadConversationHistory(conversationId: string, token: string): Promise<Message[]>`
   - GET from `/api/chat/conversations/${conversationId}/messages`
   - Include Authorization header
   - Return message array
   - **Files**: `frontend/lib/chatApi.ts`
   - **Dependencies**: Task 8

10. **Implement deleteConversation function**
    - File: `frontend/lib/chatApi.ts`
    - Function: `deleteConversation(conversationId: string, token: string): Promise<void>`
    - DELETE to `/api/chat/conversations/${conversationId}`
    - Include Authorization header
    - **Files**: `frontend/lib/chatApi.ts`
    - **Dependencies**: Task 9

**Checkpoint**: API client ready for use in components

---

### Phase 3: Chat Components

**Goal**: Build reusable UI components for chat interface

**Tasks**:

11. **Create ChatMessage component**
    - File: `frontend/components/chat/ChatMessage.tsx`
    - Props: role, content, timestamp
    - Styling: Role-based (user: right/blue, assistant: left/dark, system: center/gray)
    - Use Tailwind classes matching Phase II theme
    - Display relative timestamp (e.g., "2 min ago")
    - **Files**: `frontend/components/chat/ChatMessage.tsx`
    - **Dependencies**: Task 6

12. **Create ConfirmationModal component**
    - File: `frontend/components/chat/ConfirmationModal.tsx`
    - Props: isOpen, prompt, action, params, onConfirm, onCancel
    - UI: Modal overlay, centered dialog, confirm/cancel buttons
    - Styling: Match Phase II modal styles (if exists) or create minimal modal
    - **Files**: `frontend/components/chat/ConfirmationModal.tsx`
    - **Dependencies**: Task 11

13. **Create ChatInterface component (part 1: state)**
    - File: `frontend/components/chat/ChatInterface.tsx`
    - State: messages, conversationId, loading, error, confirmationRequest
    - Initialize: Load conversation_id from localStorage on mount
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 12

14. **Implement ChatInterface: loadHistory**
    - Method: Load message history on mount if conversation_id exists
    - Call: `loadConversationHistory(conversationId, token)`
    - Update messages state
    - Handle errors (404 → clear localStorage, start new)
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 13

15. **Implement ChatInterface: handleSendMessage**
    - Method: Send message to backend
    - Get token from auth utilities
    - Call: `sendChatMessage({message, conversation_id}, token)`
    - Handle response: Update messages, save conversation_id to localStorage
    - Handle confirmation: Set confirmationRequest state if requires_confirmation
    - Handle errors: Display as system message
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 14

16. **Implement ChatInterface: handleConfirmation**
    - Method: Handle confirmation modal actions
    - On Confirm: Send confirm_action to backend, display result
    - On Cancel: Close modal, show "Action cancelled" system message
    - Clear confirmationRequest state
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 15

17. **Implement ChatInterface: startNewConversation**
    - Method: Clear conversation state
    - Clear messages array
    - Clear conversationId state
    - Remove from localStorage
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 16

18. **Integrate ChatKit into ChatInterface**
    - Wrap with ChatKitProvider (domainKey from env)
    - Use ChatView component with messages, onSend, isLoading
    - Configure theme to match Phase II (dark mode)
    - Add message history display (map messages to ChatMessage components)
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 17

**Checkpoint**: Chat components functional and ready for page integration

---

### Phase 4: Pages & Navigation

**Goal**: Create chat page and integrate with navigation

**Tasks**:

19. **Create chat page**
    - File: `frontend/app/chat/page.tsx`
    - Import ChatInterface component
    - Add auth check (redirect if not authenticated)
    - Add page layout (header with "AI Chat Assistant" title, logout button)
    - Add "New Chat" button (calls startNewConversation)
    - **Files**: `frontend/app/chat/page.tsx`
    - **Dependencies**: Task 18

20. **Add chat link to dashboard**
    - File: `frontend/app/dashboard/page.tsx`
    - Add "AI Chat" button/link in header or sidebar
    - Use existing NeonButton component if available
    - Link to: `/chat`
    - Keep existing task UI for backward compatibility
    - **Files**: `frontend/app/dashboard/page.tsx`
    - **Dependencies**: Task 19

**Checkpoint**: Chat page accessible via navigation

---

### Phase 5: Integration & Polish

**Goal**: Error handling, edge cases, final integration

**Tasks**:

21. **Implement error handling**
    - Display errors as system messages (red text)
    - Add retry button for failed requests
    - Handle 401: Clear token, redirect to /login
    - Handle 403/404: Display error message
    - Handle network errors: Show retry option
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 20

22. **Implement loading states**
    - Show "thinking..." while waiting for response
    - Disable input during loading
    - Use ChatKit isLoading prop
    - Add typing indicator (if ChatKit supports)
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 21

23. **Add auto-scroll behavior**
    - Scroll to bottom on new message
    - Use useEffect with messages dependency
    - Smooth scroll behavior
    - **Files**: `frontend/components/chat/ChatInterface.tsx`
    - **Dependencies**: Task 22

24. **Test localStorage persistence**
    - Verify conversation_id saves after first message
    - Verify conversation_id loads on page mount
    - Verify messages persist across refreshes
    - Verify "New Chat" clears localStorage
    - **Files**: None (verification)
    - **Dependencies**: Task 23

25. **Test auth integration**
    - Verify JWT token included in requests
    - Verify 401 redirects to /login
    - Verify unauthenticated users redirected from /chat
    - **Files**: None (verification)
    - **Dependencies**: Task 24

26. **Test mobile responsive**
    - Verify layout works on small screens
    - Verify messages stack properly
    - Verify input box accessible
    - Verify buttons clickable
    - **Files**: None (verification)
    - **Dependencies**: Task 25

**Checkpoint**: All features functional and tested

---

### Phase 6: Documentation & Validation

**Goal**: Update docs and validate against success criteria

**Tasks**:

27. **Update README**
    - Document /chat route
    - Document environment variables (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
    - Document ChatKit setup
    - Add usage examples
    - **Files**: `frontend/README.md` or root README
    - **Dependencies**: Task 26

28. **Final validation checklist**
    - ✅ ChatKit renders messages correctly
    - ✅ Messages send to backend and display responses
    - ✅ Conversation persists across refreshes
    - ✅ Confirmation modal appears for delete operations
    - ✅ Errors display as system messages
    - ✅ Auth integration works (401 redirect)
    - ✅ "New Chat" clears conversation
    - ✅ Mobile responsive
    - ✅ No console errors
    - ✅ Phase II dashboard still accessible
    - **Files**: None (checklist)
    - **Dependencies**: Task 27

---

## Task Dependency Graph

```
Phase 0: [1] → [2] → [3]
Phase 1: [1] → [4] → [6], [5] (parallel)
Phase 2: [3,6] → [7] → [8] → [9] → [10]
Phase 3: [6,10] → [11] → [12] → [13] → [14] → [15] → [16] → [17] → [18]
Phase 4: [18] → [19] → [20]
Phase 5: [20] → [21] → [22] → [23] → [24] → [25] → [26]
Phase 6: [26] → [27] → [28]
```

**Critical Path**: Tasks 1-4-6-7-8-11-13-18-19-20-21-26-28

**Parallelizable**: Task 5 (env vars) can run parallel with Task 4

---

## Research Plan (Phase 0)

### Research 1: ChatKit Integration Patterns

**Question**: How to integrate OpenAI ChatKit with Next.js App Router?

**Research Steps**:
1. Check npm for `@openai/chatkit` package
2. Review ChatKit documentation (if available)
3. Identify required props and configuration
4. Determine message format compatibility

**Expected Findings**:
- ChatKitProvider wrapper component
- ChatView main component with messages, onSend, isLoading props
- Message format: {id, role, content, createdAt}
- Theme configuration for dark mode

**Alternative if ChatKit unavailable**:
- Build custom chat UI with React components
- Use existing Phase II UI patterns
- Focus on functionality over ChatKit branding

### Research 2: Phase II Frontend Patterns

**Question**: What Phase II components and utilities can be reused?

**Research Steps**:
1. Examine lib/auth.ts for token management
2. Examine lib/api.ts for API client patterns
3. Review Tailwind configuration
4. Identify reusable UI components (buttons, modals)

**Expected Findings**:
- getToken(), isAuthenticated(), clearToken() functions
- apiClient() function with auth headers
- Cyberpunk theme variables (neon-blue, cyber-surface, etc.)
- NeonButton, ConfirmModal components (if exist)

### Research 3: localStorage Best Practices

**Question**: How to safely persist conversation_id without leaking data?

**Research Steps**:
1. Review localStorage API
2. Determine key naming convention
3. Handle edge cases (storage quota, incognito mode)

**Expected Findings**:
- Key: `phase3_conversation_id`
- Store only UUID (minimal space)
- Clear on logout
- Handle QuotaExceededError gracefully

---

## Data Model (Phase 1)

### Frontend Entities (TypeScript Interfaces)

**ChatMessage** (in-memory only):
```typescript
interface ChatMessage {
  id: string;                 // UUID from backend or local ID
  role: 'user' | 'assistant' | 'system';
  content: string;            // Message text
  timestamp: Date;            // Display timestamp
}
```

**ConversationState** (React state):
```typescript
interface ConversationState {
  messages: ChatMessage[];
  conversationId: string | null;
  loading: boolean;
  error: string | null;
  confirmationRequest: ConfirmationDetails | null;
}
```

**ConfirmationDetails**:
```typescript
interface ConfirmationDetails {
  action: string;             // e.g., "delete_task"
  params: Record<string, any>; // e.g., {task_id: "uuid"}
  prompt: string;             // Display text
}
```

**No database models** (frontend doesn't manage data, only displays).

---

## API Contracts (Phase 1)

### Frontend → Backend Contracts

**Contract 1: Send Chat Message**
```
POST /api/chat
Headers: Authorization: Bearer <jwt>
Body: {
  message: string,
  conversation_id?: string,
  confirm_action?: {action: string, params: object}
}
Response: {
  message: string,
  conversation_id: string,
  requires_confirmation: boolean,
  confirmation_details?: object
}
```

**Contract 2: Load Conversation History**
```
GET /api/chat/conversations/{id}/messages
Headers: Authorization: Bearer <jwt>
Response: [{id, role, content, created_at}, ...]
```

**Contract 3: Delete Conversation**
```
DELETE /api/chat/conversations/{id}
Headers: Authorization: Bearer <jwt>
Response: {success: boolean, message: string}
```

**Contract 4: List Conversations**
```
GET /api/chat/conversations
Headers: Authorization: Bearer <jwt>
Response: [{id, title, created_at, updated_at}, ...]
```

**Note**: All contracts already implemented in backend (Spec A). Frontend consumes only.

---

## Quickstart Scenarios (Phase 1)

### Scenario 1: First-Time Chat User

**Given**: User is logged in, navigates to /chat for first time
**When**: User types "create a task called Buy groceries"
**Then**:
1. Message sent to backend
2. Backend creates task via MCP
3. Assistant responds "I've created a task called 'Buy groceries' for you."
4. conversation_id saved to localStorage
5. User can continue conversation with context

**Verification**:
- Check localStorage: `phase3_conversation_id` exists
- Check backend DB: conversation and 2 messages (user + assistant) exist
- Check UI: Both messages displayed in chat

### Scenario 2: Returning User

**Given**: User has existing conversation_id in localStorage
**When**: User navigates to /chat
**Then**:
1. conversation_id loaded from localStorage
2. Message history fetched from backend
3. Previous messages displayed
4. User can send new message with context

**Verification**:
- Check UI: Previous messages displayed
- Check network: GET request to /conversations/{id}/messages
- Check: New message includes conversation_id

### Scenario 3: Confirmation Workflow

**Given**: User is in active conversation
**When**: User types "delete task abc-123"
**Then**:
1. Backend returns requires_confirmation: true
2. ConfirmationModal appears
3. User clicks "Confirm"
4. Frontend sends confirm_action to backend
5. Backend deletes task
6. Assistant responds "Task deleted successfully"

**Verification**:
- Check UI: Modal appears with confirmation prompt
- Check network: Second POST with confirm_action
- Check backend DB: Task deleted

### Scenario 4: Error Handling

**Given**: Backend is unreachable or returns error
**When**: User sends message
**Then**:
1. Request fails
2. Error displayed as system message (red text)
3. Retry button shown
4. User clicks retry → message resent

**Verification**:
- Check UI: Error message displayed
- Check: Input not cleared (message preserved)
- Check: Retry button functional

### Scenario 5: New Chat

**Given**: User has existing conversation
**When**: User clicks "New Chat" button
**Then**:
1. localStorage cleared
2. conversationId set to null
3. Messages array cleared
4. Next message creates new conversation

**Verification**:
- Check localStorage: `phase3_conversation_id` removed
- Check UI: Messages cleared
- Check: Next message gets new conversation_id

---

## Risk Mitigation

| Risk | Mitigation Strategy | Contingency |
|------|-------------------|-------------|
| **ChatKit package unavailable** | Verify npm package in Phase 0 research | Build custom chat UI with React |
| **ChatKit API incompatible** | Review documentation in Phase 0 | Use alternative chat library (react-chatbox, etc.) |
| **localStorage blocked (incognito)** | Catch QuotaExceededError, use in-memory fallback | Conversation lost on refresh (acceptable for Phase III) |
| **Backend latency > 3s** | Show loading indicator, timeout at 10s | Display timeout error, allow retry |
| **401 during chat** | Clear token, redirect to /login | User re-authenticates |
| **Confirmation modal conflicts with Phase II** | Use different modal component or inline confirmation | Acceptable UX degradation |

---

## Success Metrics

**Functional**:
- ✅ User sends message → receives AI response
- ✅ Conversation persists across page refreshes
- ✅ Confirmation modal appears for delete operations
- ✅ Errors display gracefully with retry option
- ✅ "New Chat" creates fresh conversation

**Non-Functional**:
- ✅ Page load < 1s (excluding API calls)
- ✅ Message send < 500ms (before backend response)
- ✅ Mobile responsive (messages readable)
- ✅ No console errors
- ✅ Keyboard accessible (Tab, Enter)

**Constitution Compliance**:
- ✅ AI-First: Chat is primary interface
- ✅ Stateless: No business logic, only display
- ✅ Reusable Intelligence: Phase II auth/styles reused
- ✅ Conversation Preservation: localStorage + backend DB

---

## Implementation Strategy

**Timeline Estimate**:
- **Phase 0 (Research)**: 30 mins (3 research tasks)
- **Phase 1 (Setup)**: 15 mins (3 tasks)
- **Phase 2 (API Client)**: 1 hour (4 tasks)
- **Phase 3 (Components)**: 3 hours (8 tasks)
- **Phase 4 (Pages)**: 30 mins (2 tasks)
- **Phase 5 (Integration)**: 1.5 hours (6 tasks)
- **Phase 6 (Documentation)**: 30 mins (2 tasks)

**Total**: 7-8 hours (28 tasks)

**Sequential Approach**:
1. Research ChatKit integration (critical path)
2. Install dependencies
3. Build API client (enables component development)
4. Build components bottom-up (Message → Modal → Interface)
5. Create page and navigation
6. Test and polish

**Validation Points**:
- After Phase 1: Dependencies installed, imports work
- After Phase 2: API client can communicate with backend
- After Phase 3: Components render correctly
- After Phase 4: Chat page accessible and functional
- After Phase 5: All features working
- After Phase 6: Documentation complete

---

## Next Steps

1. Execute Phase 0 research (3 tasks)
2. Generate research.md with findings
3. Execute Phase 1 design (generate data-model.md, contracts/)
4. Run `/sp.tasks` to generate detailed tasks.md
5. Run `/sp.implement` to execute implementation
6. Manual testing with backend integration
7. Deploy to Vercel with environment variables

---

**Plan Status**: ✅ Ready for Research Phase
**Estimated Complexity**: 28 tasks across 6 phases
**Execution Mode**: Sequential with research-first approach
