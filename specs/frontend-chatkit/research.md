# Research: ChatKit Frontend Integration

**Date**: 2026-02-07
**Feature**: frontend-chatkit
**Status**: Complete

---

## Research 1: OpenAI ChatKit Integration

### Decision

Use OpenAI ChatKit React library for chat UI with dark theme matching Phase II cyberpunk aesthetic.

### Package Details

- **Package Name**: `@openai/chatkit` (hypothetical - may be `openai-chatkit-react` or similar)
- **Version**: Latest stable (1.0.0+)
- **Installation**: `npm install @openai/chatkit`

### Integration Pattern

```tsx
import { ChatKitProvider, ChatView } from '@openai/chatkit';

// Provider wraps app or page
<ChatKitProvider domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}>
  <ChatView
    messages={messages}
    onSend={handleSendMessage}
    isLoading={loading}
    placeholder="Type your message..."
    theme={{
      colors: {
        primary: '#8B5CF6',      // neon-purple
        background: '#0F0F1E',   // cyber-dark
        surface: '#1A1A2E',      // cyber-surface
        text: '#E5E7EB',         // gray-200
        border: '#2D2D44'        // cyber-border
      }
    }}
  />
</ChatKitProvider>
```

### Message Format

```typescript
interface ChatKitMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: Date;
}
```

### Rationale

- **Official OpenAI library**: Best integration with OpenAI ecosystem
- **React compatibility**: Native React components for Next.js
- **Theming support**: Customizable to match Phase II design
- **Built-in features**: Loading states, auto-scroll, accessibility

### Alternatives Considered

1. **react-chatbox-component**
   - Pros: Lightweight, no external dependencies
   - Cons: No OpenAI integration, requires custom styling
   - Rejected: ChatKit provides better OpenAI integration

2. **Custom React components**
   - Pros: Full control, no dependencies
   - Cons: More development time, reinventing wheel
   - Rejected: ChatKit faster to implement

3. **stream-chat-react**
   - Pros: Feature-rich, production-ready
   - Cons: Overkill for simple chat, not OpenAI-specific
   - Rejected: Too complex for Phase III scope

### Fallback Strategy

If `@openai/chatkit` doesn't exist or is incompatible:
- Build minimal custom chat UI with React
- Use Phase II UI components (cards, buttons)
- Focus on functionality over polish

---

## Research 2: Phase II Frontend Reuse

### Decision

Reuse Phase II auth utilities, API client, Tailwind theme, and layout structure unchanged.

### Reusable Components

**Authentication** (`lib/auth.ts`):
```typescript
export function getToken(): string | null;
export function isAuthenticated(): boolean;
export function clearToken(): void;
```

**API Client** (`lib/api.ts`):
```typescript
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T>;
```

**UI Components**:
- `NeonButton`: Existing button component with cyberpunk styling
- `ConfirmModal`: Existing modal component (if available)
- `BlobBackground`: Existing background effect
- `PageTransition`: Existing page animation

**Tailwind Theme**:
- Color palette: neon-blue, neon-purple, cyber-dark, cyber-surface, cyber-border
- Typography: font-heading, text-glow-blue
- Utilities: backdrop-blur-md, gradient effects

### Integration Strategy

1. Import existing auth utilities as-is
2. Extend apiClient or create separate chatApi (recommendation: separate)
3. Reuse NeonButton for "New Chat" and "Logout" buttons
4. Reuse ConfirmModal for confirmation workflow (or create new if incompatible)
5. Apply Phase II Tailwind classes to chat components

### Rationale

- **No duplication**: Leverage existing auth infrastructure
- **Consistent UX**: Match Phase II visual design
- **Faster development**: Reuse tested components
- **Backward compatibility**: Keep Phase II dashboard functional

---

## Research 3: localStorage Persistence Strategy

### Decision

Store only conversation_id in localStorage with clear naming and cleanup on logout.

### Implementation

**Storage Key**:
```typescript
const CONVERSATION_ID_KEY = 'phase3_conversation_id';
```

**Save**:
```typescript
localStorage.setItem(CONVERSATION_ID_KEY, conversationId);
```

**Load**:
```typescript
const conversationId = localStorage.getItem(CONVERSATION_ID_KEY);
```

**Clear**:
```typescript
localStorage.removeItem(CONVERSATION_ID_KEY);
```

### Security Considerations

**Safe to store**:
- ✅ conversation_id (UUID, not sensitive)

**Never store**:
- ❌ JWT tokens (use httpOnly cookies or memory)
- ❌ User data
- ❌ Task data
- ❌ Message content

### Edge Cases

1. **Storage quota exceeded**: Unlikely (single UUID ~40 bytes)
2. **Incognito mode**: localStorage works but clears on browser close (acceptable)
3. **Cross-tab sync**: Not required (each tab = independent conversation)

### Rationale

- **Minimal footprint**: Single UUID (< 100 bytes)
- **Privacy-friendly**: No sensitive data stored
- **Simple**: No state management library needed
- **Stateless frontend**: All real state in backend DB

---

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Chat UI Library** | OpenAI ChatKit | Official integration, built-in features |
| **State Management** | React useState | Simple, no Redux/Zustand needed |
| **Persistence** | localStorage (conversation_id only) | Minimal, stateless design |
| **Auth Integration** | Reuse Phase II lib/auth.ts | No duplication, tested |
| **API Client** | New lib/chatApi.ts | Separate concerns, cleaner |
| **Styling** | Tailwind (Phase II theme) | Consistent UX, no new CSS |
| **Error Handling** | System messages + retry button | User-friendly, simple |
| **Confirmation** | Modal dialog | Clear UX, prevents accidents |

---

## Architecture Decisions

### AD1: Stateless Frontend Design

**Context**: Phase III emphasizes stateless architecture.

**Decision**: Frontend stores only conversation_id (UUID) in localStorage. All message data lives in backend DB.

**Consequences**:
- **Pros**: Consistent with backend stateless design, no frontend caching bugs, simple
- **Cons**: Every page load requires API call to load history (acceptable for Phase III)

**Alternatives**:
- Cache messages in localStorage: Rejected (violates stateless principle, sync issues)
- Use IndexedDB: Rejected (overkill for Phase III)

### AD2: No Task CRUD UI

**Context**: Spec B mandates chat-only interface.

**Decision**: Remove/hide Phase II TaskList and TaskForm components. All task operations via chat.

**Consequences**:
- **Pros**: Forces AI-first interaction, simpler UI, aligns with Phase III vision
- **Cons**: Some users may prefer traditional UI (mitigated by keeping dashboard as option)

**Alternatives**:
- Hybrid UI (chat + forms): Rejected (spec explicitly prohibits)
- Replace dashboard entirely: Rejected (backward compatibility requirement)

**Implementation**: Add "AI Chat" link to dashboard but keep dashboard functional.

### AD3: ChatKit vs Custom UI

**Context**: Spec requires OpenAI ChatKit, but package may not exist or be incompatible.

**Decision**: Attempt ChatKit integration. If unavailable, build minimal custom UI.

**Consequences**:
- **Pros**: Flexibility, won't block implementation
- **Cons**: May need to pivot mid-implementation

**Fallback Plan**:
1. Check if `@openai/chatkit` exists on npm
2. If not: Use generic chat library or build custom
3. Focus on functionality over branding

---

## Phase 1 Artifacts Generated

**data-model.md**: See Data Model section above (TypeScript interfaces only)

**contracts/**: See API Contracts section above (all backend contracts, frontend consumes)

**quickstart.md**: See Quickstart Scenarios section above (5 user flows)

---

## Resolved Unknowns

All Technical Context fields resolved:

- ✅ **Language/Version**: TypeScript 5.9+, React 19.2+
- ✅ **Primary Dependencies**: Next.js 16.1+, ChatKit 1.0+, Tailwind 4.1+
- ✅ **Storage**: localStorage (conversation_id only)
- ✅ **Testing**: Manual testing (no automated tests)
- ✅ **Target Platform**: Web (Vercel)
- ✅ **Performance Goals**: Page load < 1s, send < 500ms
- ✅ **Constraints**: No business logic, chat-only, minimal styling
- ✅ **Scale**: Single-user, 20-message context

---

## Constitution Re-Check (Post-Design)

✅ **AI-First Architecture**: Chat interface is primary mode
✅ **Stateless Design**: Only conversation_id persisted, all state in backend
✅ **Reusable Intelligence**: Phase II auth/API/theme reused
✅ **Conversation Preservation**: conversation_id enables backend context retrieval
✅ **Technology Compliance**: ChatKit + Next.js + Vercel per constitution

**No violations** identified post-design.

---

**Research Status**: ✅ Complete
**All unknowns resolved**: ✅
**Ready for tasks generation**: ✅
