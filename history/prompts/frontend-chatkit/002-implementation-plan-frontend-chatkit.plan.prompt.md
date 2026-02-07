---
id: 002
title: Implementation plan for ChatKit frontend integration
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: frontend-chatkit
branch: main
user: system
command: /sp.plan
labels: ["planning", "frontend", "chatkit", "nextjs", "conversational-ui"]
links:
  spec: specs/frontend-chatkit/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/frontend-chatkit/plan.md
 - specs/frontend-chatkit/research.md
 - specs/frontend-chatkit/spec.md (moved from specs/spec-B-frontend-chatkit.md)
tests:
 - (manual testing checklist in plan.md)
---

## Prompt

/sp.plan

(No additional user input - executed directly after /sp.specify for Spec B)

## Response snapshot

Created comprehensive implementation plan with 28 tasks across 6 phases:

**Phase 0: Preparation & Research (3 tasks)**
- Research 1: ChatKit integration patterns (package, API, theming)
- Research 2: Phase II frontend reuse (auth, API client, Tailwind, components)
- Research 3: localStorage persistence strategy (conversation_id only)

**Phase 1: Setup & Dependencies (3 tasks)**
- Install @openai/chatkit package
- Configure environment variables (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- Verify ChatKit imports work

**Phase 2: API Client Layer (4 tasks)**
- Create chat API types (ChatMessage, ChatRequest, ChatResponse, ConfirmationDetails)
- Implement sendChatMessage function
- Implement loadConversationHistory function
- Implement deleteConversation function

**Phase 3: Chat Components (8 tasks)**
- Create ChatMessage component (role-based styling)
- Create ConfirmationModal component (modal dialog)
- Create ChatInterface component with state management
- Implement loadHistory method
- Implement handleSendMessage method
- Implement handleConfirmation method
- Implement startNewConversation method
- Integrate ChatKit into ChatInterface

**Phase 4: Pages & Navigation (2 tasks)**
- Create /chat page with ChatInterface
- Add "AI Chat" link to dashboard

**Phase 5: Integration & Polish (6 tasks)**
- Implement error handling (system messages, retry)
- Implement loading states
- Add auto-scroll behavior
- Test localStorage persistence
- Test auth integration
- Test mobile responsive

**Phase 6: Documentation & Validation (2 tasks)**
- Update README with chat documentation
- Final validation checklist (10 criteria)

**Research Findings**:

*ChatKit Integration*:
- Package: @openai/chatkit (hypothetical, may vary)
- Components: ChatKitProvider, ChatView
- Message format: {id, role, content, createdAt}
- Theme support: Custom colors matching Phase II
- Fallback: Custom React UI if ChatKit unavailable

*Phase II Reuse*:
- Auth utilities: getToken, isAuthenticated, clearToken
- API client: apiClient function with auth headers
- UI components: NeonButton, ConfirmModal (if exists), BlobBackground
- Tailwind theme: neon-blue, neon-purple, cyber-dark, cyber-surface

*localStorage Strategy*:
- Key: phase3_conversation_id
- Store: Only UUID (40 bytes)
- Security: No sensitive data
- Clear: On logout or "New Chat"

**Architecture Decisions**:

*AD1: Stateless Frontend*
- Store only conversation_id in localStorage
- All messages in backend DB
- Pros: Consistent with backend, no sync issues
- Cons: API call on page load (acceptable)

*AD2: No Task CRUD UI*
- Chat-only interface per spec
- Keep Phase II dashboard for backward compatibility
- Pros: Forces AI-first interaction
- Cons: Some users may prefer traditional UI (mitigated by dashboard option)

*AD3: ChatKit vs Custom UI*
- Attempt ChatKit integration
- Fallback to custom React UI if unavailable
- Pros: Flexibility, won't block implementation
- Cons: May need mid-implementation pivot

**Data Model** (TypeScript interfaces):
- ChatMessage: id, role, content, timestamp
- ConversationState: messages, conversationId, loading, error, confirmationRequest
- ConfirmationDetails: action, params, prompt
- No database models (frontend display only)

**API Contracts** (all implemented in backend):
- POST /api/chat: Send message with optional conversation_id
- GET /api/chat/conversations/{id}/messages: Load history
- DELETE /api/chat/conversations/{id}: Delete conversation
- GET /api/chat/conversations: List conversations

**Quickstart Scenarios**:
1. First-time user: Send message → conversation created → saved to localStorage
2. Returning user: Load conversation_id → fetch history → display messages
3. Confirmation: Delete request → modal → confirm → execute
4. Error handling: Network error → display → retry
5. New chat: Clear localStorage → fresh conversation

**Task Organization**:
- Research-first approach (resolve unknowns)
- Bottom-up component development (Message → Modal → Interface)
- Page integration after components ready
- Testing and polish at end

**Timeline**: 7-8 hours (28 tasks)

**Dependencies**:
- Spec A backend (implemented ✅)
- Phase II auth utilities (existing ✅)
- Phase II Tailwind theme (existing ✅)
- ChatKit package (to be verified in Phase 0)

**Constitution Compliance**:
✅ AI-First Architecture (chat primary interface)
✅ Stateless Design (only conversation_id persisted)
✅ Reusable Intelligence (Phase II auth/styles reused)
✅ Conversation Preservation (localStorage + backend DB)
✅ Technology Stack Compliance (ChatKit + Next.js + Vercel)

## Outcome

- ✅ Impact: Complete implementation plan with research-driven approach
- 🧪 Tests: Manual testing strategy with 5 quickstart scenarios
- 📁 Files: Created plan.md and research.md, organized spec into feature directory
- 🔁 Next prompts: Run /sp.tasks to generate detailed tasks.md, then /sp.implement
- 🧠 Reflection: Plan emphasizes reuse of Phase II infrastructure, minimal new code, stateless design. Research phase resolves ChatKit integration questions. Clear fallback strategy if ChatKit unavailable.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning successful with research phase
- Graders run and results (PASS/FAIL): Architecture compliance: PASS (stateless, AI-first, reusable intelligence)
- Prompt variant (if applicable): Standard /sp.plan with Phase 0 research included
- Next experiment (smallest change to try): Run /sp.tasks to generate executable task list
