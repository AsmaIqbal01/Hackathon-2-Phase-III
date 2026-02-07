# Spec B: ChatKit-Based Frontend for Todo AI Chatbot

**Version:** 1.0
**Status:** Draft
**Owner:** Phase III Frontend Team
**Context:** Phase III frontend layer using OpenAI ChatKit to provide conversational interface for AI-powered task management.

---

## 1. Overview

### 1.1 Objective

Replace Phase II traditional CRUD UI with conversational chat interface powered by OpenAI ChatKit. Users manage tasks through natural language instead of forms/buttons.

### 1.2 Architecture

```
User → ChatKit UI → Next.js API Route → Backend /api/chat → Master Agent → MCP → DB
```

### 1.3 Scope

**In Scope**:
- Chat interface with message history
- Natural language task management
- Conversation persistence (client-side conversation_id)
- Loading states and error handling
- Authentication integration
- Tool call transparency (optional system messages)

**Out of Scope**:
- Task list/grid views (all interactions via chat)
- Task CRUD forms (create/edit/delete buttons)
- Filtering/sorting UI controls
- Task visualization (charts, stats)
- Real-time collaboration
- Voice input
- File attachments
- Advanced ChatKit features (streaming, plugins)

---

## 2. Backend Contract (Already Implemented)

### 2.1 Chat Endpoint

**POST /api/chat**

Request:
```json
{
  "message": "create a task called Buy groceries",
  "conversation_id": "uuid-here" | null,
  "confirm_action": {
    "action": "delete_task",
    "params": {"task_id": "uuid"}
  } | null
}
```

Response:
```json
{
  "message": "I've created a task called 'Buy groceries' for you.",
  "conversation_id": "uuid-here",
  "requires_confirmation": false,
  "confirmation_details": {
    "action": "delete_task",
    "params": {"task_id": "uuid"}
  } | null
}
```

**Headers**:
- `Authorization: Bearer <jwt_token>`

### 2.2 Conversation Management

**GET /api/chat/conversations**
- Returns: `[{id, title, created_at, updated_at}, ...]`

**GET /api/chat/conversations/{id}/messages**
- Returns: `[{id, role, content, created_at}, ...]`

**DELETE /api/chat/conversations/{id}**
- Returns: `{success: true, message: "..."}`

---

## 3. Technology Stack

### 3.1 Core Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.1+ | React framework (App Router) |
| **React** | 19.2+ | UI library |
| **OpenAI ChatKit** | Latest | Chat UI component |
| **TypeScript** | 5.9+ | Type safety |
| **Tailwind CSS** | 4.1+ | Styling (existing from Phase II) |

### 3.2 New Dependencies

Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0"
  }
}
```

### 3.3 Environment Variables

Add to `frontend/.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key
```

---

## 4. Frontend Architecture

### 4.1 File Structure

```
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx           # [NEW] Chat interface page
│   ├── dashboard/
│   │   └── page.tsx           # [MODIFIED] Add link to chat page
│   └── layout.tsx             # [REUSED] Existing layout
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx  # [NEW] Main chat component
│   │   ├── ChatMessage.tsx    # [NEW] Individual message component
│   │   └── ConfirmationModal.tsx # [NEW] Confirmation dialog
│   ├── TaskList.tsx           # [REUSED] Phase II (kept for reference)
│   └── TaskForm.tsx           # [REUSED] Phase II (kept for reference)
└── lib/
    ├── chatApi.ts             # [NEW] Chat API client
    ├── api.ts                 # [REUSED] Phase II API client
    └── auth.ts                # [REUSED] Phase II auth utilities
```

### 4.2 Component Hierarchy

```
ChatInterface
├── ChatKit wrapper
├── Message history
│   └── ChatMessage (repeated)
├── Confirmation modal
│   └── ConfirmationModal
└── Input area (ChatKit built-in)
```

---

## 5. Functional Requirements

### 5.1 Chat Interface (Primary Feature)

**FR1: Message Input**
- User types message in input box
- Send button or Enter key submits message
- Input clears after sending
- Disabled during loading

**FR2: Message Display**
- User messages: Right-aligned, distinct color
- Assistant messages: Left-aligned, different color
- System messages: Centered, subtle styling (for tool transparency)
- Timestamps: Show relative time (e.g., "2 minutes ago")
- Auto-scroll to latest message

**FR3: Message History**
- Display all messages in conversation
- Scrollable container (max height with overflow)
- Oldest messages at top, newest at bottom
- Persist across page refreshes (via conversation_id in localStorage)

**FR4: Conversation Continuity**
- Store conversation_id in localStorage on first message
- Include conversation_id in subsequent requests
- Load message history on page load (if conversation_id exists)
- Clear conversation button (creates new conversation)

**FR5: Loading States**
- Show "thinking..." indicator while waiting for response
- Disable input during processing
- Show typing indicator for assistant

**FR6: Error Handling**
- Display error messages as system messages (red/warning color)
- Retry button for failed requests
- Graceful handling of network errors, 401 (redirect to login), 500 errors

### 5.2 Confirmation Workflow

**FR7: Confirmation Dialog**
- When `requires_confirmation: true` in response:
  - Display modal with confirmation prompt
  - Show action details (e.g., "Delete task: Buy groceries")
  - Confirm and Cancel buttons
- On Confirm:
  - Send POST /api/chat with `confirm_action` parameter
  - Display result message
- On Cancel:
  - Close modal, show "Action cancelled" system message

### 5.3 Tool Transparency (Optional)

**FR8: Tool Call Visibility**
- When assistant uses tools, show subtle system message:
  - "Creating task..."
  - "Listing tasks..."
  - "Marking task as completed..."
  - "Deleting task..."
- Appears between user message and assistant response
- Distinct styling (italic, gray text, small font)

### 5.4 Authentication Integration

**FR9: Auth Check**
- Redirect to /login if not authenticated
- Include JWT token in all API requests
- Handle 401 errors (clear token, redirect to login)

### 5.5 Navigation

**FR10: Access Point**
- Add "AI Chat" link in dashboard navigation
- Route: `/chat`
- Accessible from Phase II dashboard page

---

## 6. ChatKit Integration

### 6.1 Setup

```tsx
import { ChatKitProvider, ChatView } from '@openai/chatkit';

// In layout or provider
<ChatKitProvider domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}>
  <ChatView />
</ChatKitProvider>
```

### 6.2 Configuration

**ChatKit Props**:
```tsx
<ChatView
  messages={messages}
  onSend={handleSendMessage}
  isLoading={loading}
  placeholder="Ask me to create, update, or manage your tasks..."
  theme="dark" // Match Phase II cyberpunk theme
/>
```

### 6.3 Message Format

```typescript
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}
```

---

## 7. API Integration

### 7.1 Chat API Client

File: `frontend/lib/chatApi.ts`

```typescript
export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
  confirm_action?: {
    action: string;
    params: Record<string, any>;
  } | null;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  requires_confirmation: boolean;
  confirmation_details?: {
    action: string;
    params: Record<string, any>;
  } | null;
}

export async function sendChatMessage(
  request: ChatRequest,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Chat request failed');
  }

  return response.json();
}

export async function loadConversationHistory(
  conversationId: string,
  token: string
): Promise<Message[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/conversations/${conversationId}/messages`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to load conversation history');
  }

  return response.json();
}

export async function deleteConversation(
  conversationId: string,
  token: string
): Promise<void> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat/conversations/${conversationId}`,
    {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to delete conversation');
  }
}
```

---

## 8. Component Specifications

### 8.1 ChatInterface Component

File: `frontend/components/chat/ChatInterface.tsx`

**Responsibilities**:
- Wrap ChatKit component
- Manage conversation state (messages, conversation_id)
- Handle message sending and receiving
- Manage loading and error states
- Persist conversation_id to localStorage
- Handle confirmation workflow

**State**:
```typescript
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [conversationId, setConversationId] = useState<string | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [confirmationRequest, setConfirmationRequest] = useState<any>(null);
```

**Key Methods**:
- `handleSendMessage(text: string)`: Send to backend, update state
- `loadHistory()`: Load from backend on mount
- `handleConfirmation(confirmed: boolean)`: Handle confirmation dialog
- `startNewConversation()`: Clear state, remove localStorage

### 8.2 ChatMessage Component

File: `frontend/components/chat/ChatMessage.tsx`

**Props**:
```typescript
interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}
```

**Styling**:
- User: Right-aligned, blue/purple gradient background
- Assistant: Left-aligned, dark background with border
- System: Centered, gray text, small font, italic

### 8.3 ConfirmationModal Component

File: `frontend/components/chat/ConfirmationModal.tsx`

**Props**:
```typescript
interface ConfirmationModalProps {
  isOpen: boolean;
  prompt: string;
  action: string;
  params: Record<string, any>;
  onConfirm: () => void;
  onCancel: () => void;
}
```

**UI**:
- Modal overlay (backdrop blur)
- Centered dialog box
- Prompt text
- Action details (e.g., "Deleting task: Buy groceries")
- Confirm (red/danger) and Cancel (gray) buttons

---

## 9. User Flows

### 9.1 First-Time User Flow

```
1. User logs in (Phase II auth)
2. User navigates to /chat
3. ChatInterface loads with empty state
4. User types: "create a task called Buy groceries"
5. Message sent to backend
6. Backend returns: {message: "I've created...", conversation_id: "uuid-123"}
7. Frontend stores conversation_id in localStorage
8. Assistant message displayed
9. User continues conversation with context
```

### 9.2 Returning User Flow

```
1. User navigates to /chat
2. ChatInterface reads conversation_id from localStorage
3. Load message history from GET /api/chat/conversations/{id}/messages
4. Display existing messages
5. User sends new message with conversation_id
6. Backend loads context from DB (last 20 messages)
7. Assistant responds with full context
```

### 9.3 Confirmation Flow

```
1. User: "delete task abc-123"
2. Backend returns: {requires_confirmation: true, confirmation_details: {...}}
3. Frontend shows ConfirmationModal
4. User clicks Confirm
5. Frontend sends: {confirm_action: {action: "delete_task", params: {...}}}
6. Backend executes deletion
7. Frontend displays: "Task deleted successfully"
```

### 9.4 Error Flow

```
1. User sends message
2. Network error or backend error occurs
3. Frontend catches error
4. Display error as system message (red text)
5. Show retry button
6. User clicks retry → resend message
```

---

## 10. State Management

### 10.1 Client-Side State

**Conversation State**:
```typescript
// In memory (React state)
messages: ChatMessage[]
conversationId: string | null
loading: boolean
error: string | null
confirmationRequest: ConfirmationDetails | null

// In localStorage
CONVERSATION_ID_KEY = 'phase3_conversation_id'
```

**State Persistence**:
- Save conversation_id to localStorage after first message
- Load conversation_id from localStorage on mount
- Clear localStorage on "New Chat" action

### 10.2 No Server-Side State

**Critical**: Frontend does NOT maintain:
- Task lists (no caching)
- User preferences
- Session state beyond JWT token

All state lives in:
- Backend database (conversation history, tasks)
- Client memory (current messages)
- Client localStorage (conversation_id only)

---

## 11. UI/UX Requirements

### 11.1 Layout

```
┌─────────────────────────────────────────┐
│ Header: "AI Task Assistant" | [New Chat] [Logout]
├─────────────────────────────────────────┤
│                                         │
│  Messages Area (scrollable)             │
│                                         │
│  [User message]                         │
│           [Assistant message]           │
│  [User message]                         │
│           [Assistant message]           │
│                                         │
├─────────────────────────────────────────┤
│ Input: [Type your message...]  [Send]  │
└─────────────────────────────────────────┘
```

### 11.2 Styling Requirements

**Minimal Approach**:
- Reuse Phase II Tailwind configuration
- Reuse cyberpunk theme variables (neon-blue, cyber-surface, etc.)
- No custom animations beyond Phase II
- No complex layouts or grids
- Focus: Functional and readable

**Message Styling**:
- User: `bg-gradient-to-r from-neon-blue to-neon-purple text-white`
- Assistant: `bg-cyber-surface border border-cyber-border text-gray-200`
- System: `text-gray-400 italic text-sm text-center`

**Container**:
- Max width: `max-w-4xl mx-auto`
- Padding: `p-4 sm:p-6`
- Background: `bg-cyber-surface/80 backdrop-blur-md`

### 11.3 Responsive Design

- Mobile-first approach
- Stack layout on mobile (full width messages)
- Desktop: Centered container with max width
- Input box: Fixed at bottom or inline below messages

---

## 12. ChatKit Configuration

### 12.1 Basic Setup

```tsx
import { ChatKitProvider, ChatView } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatKitProvider domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}>
      <div className="min-h-screen bg-cyber-dark">
        <ChatView
          messages={messages}
          onSend={handleSendMessage}
          isLoading={loading}
          placeholder="Ask me to create, list, update, or delete tasks..."
        />
      </div>
    </ChatKitProvider>
  );
}
```

### 12.2 Message Adapter

Convert backend messages to ChatKit format:

```typescript
function toChatKitMessage(msg: BackendMessage): ChatKitMessage {
  return {
    id: msg.id,
    role: msg.role,
    content: msg.content,
    createdAt: new Date(msg.created_at)
  };
}
```

### 12.3 Theming

Apply dark theme to match Phase II:

```tsx
<ChatView
  theme={{
    colors: {
      primary: '#8B5CF6', // neon-purple
      background: '#0F0F1E', // cyber-dark
      surface: '#1A1A2E', // cyber-surface
      text: '#E5E7EB', // gray-200
      border: '#2D2D44' // cyber-border
    }
  }}
/>
```

---

## 13. Implementation Tasks Breakdown

### 13.1 Setup & Dependencies (3 tasks)

1. Install ChatKit: `npm install @openai/chatkit`
2. Add environment variables to .env.local
3. Verify ChatKit imports work

### 13.2 API Client (2 tasks)

4. Create `lib/chatApi.ts` with sendChatMessage, loadConversationHistory, deleteConversation
5. Add TypeScript interfaces for ChatRequest/Response

### 13.3 Components (5 tasks)

6. Create ChatMessage component with role-based styling
7. Create ConfirmationModal component with confirm/cancel
8. Create ChatInterface component (main orchestration)
9. Wire up ChatKit with message state
10. Add localStorage persistence for conversation_id

### 13.4 Pages (2 tasks)

11. Create /chat page with ChatInterface
12. Add "AI Chat" link to dashboard navigation

### 13.5 Integration (3 tasks)

13. Implement handleSendMessage with backend integration
14. Implement confirmation workflow (modal + confirm_action)
15. Implement error handling and retry logic

---

## 14. Testing Strategy (Phase II Style)

### 14.1 Manual Testing Checklist

**Basic Flow**:
- [ ] User can send message and receive response
- [ ] Conversation_id persists in localStorage
- [ ] Messages persist across page refresh
- [ ] New Chat clears conversation and starts fresh

**Task Operations**:
- [ ] "Create a task called X" → Task created
- [ ] "List my tasks" → Tasks displayed in message
- [ ] "Mark task X as complete" → Task updated
- [ ] "Delete task X" → Confirmation modal → Confirm → Task deleted

**Error Handling**:
- [ ] Network error → Error message displayed
- [ ] 401 error → Redirect to login
- [ ] Invalid message → Error displayed
- [ ] OpenAI API error → Graceful error message

**Confirmation**:
- [ ] Delete request triggers confirmation modal
- [ ] Cancel → No action taken
- [ ] Confirm → Action executed

### 14.2 Integration Testing

**Not Required for Phase III**. Manual testing sufficient for MVP.

---

## 15. Design Constraints

### 15.1 No Business Logic in Frontend

**Prohibited**:
- Task validation rules
- Task status transitions
- User permission checks
- Data transformation beyond display

**Allowed**:
- Message formatting for display
- conversation_id persistence
- Loading/error state management
- UI interactions (modals, navigation)

### 15.2 No Duplicate UI Components

**Remove/Hide** (if desired):
- Phase II TaskList component (traditional grid)
- Phase II TaskForm component (create/edit forms)
- Phase II task detail modals

**Keep** (for backward compatibility):
- Dashboard page (add link to /chat)
- Auth pages (login/register)
- Layout and navigation

### 15.3 Minimal CSS

**Do NOT add**:
- Custom animations (beyond Phase II)
- Complex transitions
- Advanced hover effects
- Loading spinners (use ChatKit built-in)

**Do ADD**:
- Role-based message colors
- Confirmation modal styling
- Error message styling
- Basic responsive layout

---

## 16. Environment Configuration

### 16.1 Development

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here
```

### 16.2 Production

```bash
# Environment variables (Vercel/GitHub Pages)
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=prod-chatkit-domain-key
```

---

## 17. Error Handling Specification

### 17.1 Error Categories

| Error Source | Handling Strategy | UI Feedback |
|--------------|------------------|-------------|
| **Network error** | Catch in API client | "Connection error. Please check your internet." + Retry button |
| **401 Unauthorized** | Clear token, redirect | Redirect to /login |
| **403 Forbidden** | Display error | "Access denied. This conversation may not belong to you." |
| **404 Not Found** | Display error | "Conversation not found. Starting new chat..." |
| **500 Server Error** | Display error | "Server error. Please try again." + Retry button |
| **OpenAI API error** | Surface from backend | Display backend error message |

### 17.2 Error Display

```typescript
// System message for errors
{
  id: 'error-' + Date.now(),
  role: 'system',
  content: '⚠️ Error: ' + errorMessage,
  timestamp: new Date()
}
```

---

## 18. Performance Requirements

### 18.1 Target Metrics

- **First message send**: < 500ms (before backend response)
- **Message display**: Instant (no rendering delay)
- **Page load**: < 1s (excluding message history API call)
- **History load**: < 2s (for 20 messages)

### 18.2 Optimization

**Not Required for Phase III**:
- Message virtualization
- Lazy loading
- Image optimization (no images in Phase III)
- Code splitting

**Sufficient**:
- Basic React optimization (useCallback, useMemo for expensive operations)
- Avoid unnecessary re-renders

---

## 19. Accessibility (Basic)

**Minimum Requirements**:
- Semantic HTML (main, section, article for messages)
- Keyboard navigation (Enter to send, Tab navigation)
- ARIA labels for buttons (Send, New Chat, Logout)
- Focus management (input after send, modal focus)

**Not Required**:
- Screen reader optimization
- High contrast mode
- Keyboard shortcuts
- Focus indicators (beyond browser defaults)

---

## 20. Security Considerations

### 20.1 Token Management

**Do**:
- Send JWT token in Authorization header
- Clear token on 401 errors
- Redirect to login if unauthenticated

**Do NOT**:
- Store sensitive data in localStorage (only conversation_id)
- Log tokens to console
- Expose OPENAI_API_KEY (only use DOMAIN_KEY)

### 20.2 Input Sanitization

**Backend Responsibility**: All validation and sanitization happens in backend
**Frontend**: Display content as-is (React auto-escapes)

### 20.3 CORS

Backend already configured with CORS for `http://localhost:3000` and frontend domain.

---

## 21. Migration from Phase II

### 21.1 Dashboard Integration

**Option 1** (Recommended): Add chat link to dashboard
```tsx
// In dashboard/page.tsx
<div className="flex gap-4">
  <Link href="/chat">
    <NeonButton>AI Chat Assistant</NeonButton>
  </Link>
  {/* Keep existing task UI for backward compatibility */}
</div>
```

**Option 2**: Replace dashboard with chat
```tsx
// Redirect dashboard to chat
// In dashboard/page.tsx
useEffect(() => {
  router.push('/chat');
}, []);
```

### 21.2 Backward Compatibility

**Keep Phase II Components**:
- `/dashboard` route (traditional task UI)
- `/login` and `/register` routes
- TaskList, TaskForm components (if users prefer traditional UI)

**Rationale**: Some users may prefer traditional CRUD over chat. Provide both options.

---

## 22. Deployment Notes

### 22.1 Frontend Deployment

**Vercel** (Recommended):
```bash
# Automatic deployment from GitHub
# Set environment variables in Vercel dashboard:
# - NEXT_PUBLIC_API_BASE_URL
# - NEXT_PUBLIC_OPENAI_DOMAIN_KEY
```

**GitHub Pages** (Alternative):
```bash
# Build static export
npm run build
npm run export
# Deploy /out directory to GitHub Pages
```

### 22.2 Backend Coordination

**CORS Configuration**: Backend must allow frontend domain
**API URL**: Update NEXT_PUBLIC_API_BASE_URL to production backend URL

---

## 23. Success Criteria

### 23.1 Functional

- ✅ User can send messages and receive AI responses
- ✅ Conversation persists across page refreshes
- ✅ Confirmation workflow for delete operations
- ✅ Error messages display clearly
- ✅ Authentication integration works
- ✅ "New Chat" clears conversation

### 23.2 Non-Functional

- ✅ Page loads in < 1s
- ✅ No console errors
- ✅ Mobile responsive (messages stack properly)
- ✅ Accessible via keyboard (Tab, Enter)

### 23.3 Constitution Compliance

- ✅ **AI-First**: Chat is primary interface
- ✅ **Stateless**: No frontend state management beyond conversation_id
- ✅ **Reusable Intelligence**: Phase II auth/API utilities reused
- ✅ **Conversation Preservation**: conversation_id persisted for continuity

---

## 24. Out of Scope (Phase III)

**Explicitly Excluded**:
- Task list/grid views in chat (all via text responses)
- Rich text formatting (bold, italic, code blocks)
- Message editing or deletion
- Conversation search
- Conversation list sidebar
- User avatars or profile pictures
- Read receipts or typing indicators (beyond basic loading)
- Message reactions or emojis
- Voice input/output
- File attachments
- Image generation or display
- Multi-language support
- Dark/light mode toggle (always dark)
- Keyboard shortcuts
- Message export
- Conversation sharing

---

## 25. Dependencies on Spec A (Backend)

### 25.1 Required Backend Endpoints

- ✅ POST /api/chat (implemented in Spec A)
- ✅ GET /api/chat/conversations (implemented in Spec A)
- ✅ GET /api/chat/conversations/{id}/messages (implemented in Spec A)
- ✅ DELETE /api/chat/conversations/{id} (implemented in Spec A)

### 25.2 Backend Assumptions

- Backend is stateless (conversation context loaded from DB)
- Backend handles all task operations via MCP tools
- Backend returns natural language responses
- Backend handles confirmation workflow detection

---

## 26. Implementation Sequence

1. **Setup** (install ChatKit, configure env vars)
2. **API Client** (chatApi.ts with TypeScript interfaces)
3. **Components** (ChatMessage, ConfirmationModal)
4. **ChatInterface** (main orchestration component)
5. **Chat Page** (/chat route)
6. **Dashboard Integration** (add link to chat)
7. **Testing** (manual verification)
8. **Documentation** (README update)

---

## 27. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **ChatKit licensing/costs** | Unexpected costs | Verify ChatKit free tier limits before deployment |
| **ChatKit API changes** | Breaking changes | Pin ChatKit version in package.json |
| **localStorage limits** | Conversation_id loss | Only store UUID (minimal space), clear on logout |
| **Backend latency** | Slow chat experience | Show loading indicator, set timeout (10s) |
| **OpenAI API quota** | Chat unavailable | Surface error gracefully, provide fallback message |
| **Browser compatibility** | UI breaks | Test in Chrome, Firefox, Safari (ChatKit supports all) |

---

## 28. Validation Checklist

**Before marking complete**:
- [ ] ChatKit successfully renders messages
- [ ] Messages send to backend and display responses
- [ ] Conversation_id persists in localStorage
- [ ] Confirmation modal appears for delete operations
- [ ] Errors display as system messages
- [ ] Auth integration works (401 → redirect to login)
- [ ] "New Chat" button clears conversation
- [ ] Mobile responsive (messages readable on small screens)
- [ ] No console errors
- [ ] Phase II dashboard still accessible

---

## Appendix A: ChatKit API Reference

### A.1 Key Components

**ChatKitProvider**:
```tsx
<ChatKitProvider domainKey={string}>
  {children}
</ChatKitProvider>
```

**ChatView**:
```tsx
<ChatView
  messages={ChatMessage[]}
  onSend={(content: string) => void}
  isLoading={boolean}
  placeholder={string}
  theme={ThemeConfig}
/>
```

### A.2 Message Format

```typescript
interface ChatKitMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: Date;
}
```

---

## Appendix B: Phase II → Phase III Frontend Delta

### What's Reused (Unchanged)
- Auth pages (login, register)
- Auth utilities (lib/auth.ts)
- API client (lib/api.ts)
- Tailwind configuration
- Layout component
- Cyberpunk theme styles

### What's New (Phase III)
- ChatKit integration
- Chat page (/chat)
- Chat API client (lib/chatApi.ts)
- Chat components (ChatInterface, ChatMessage, ConfirmationModal)
- Conversation state management

### What's Modified
- Dashboard: Add link to /chat
- package.json: Add @openai/chatkit dependency
- .env.local: Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY

### What's Optional (Backward Compatibility)
- Keep Phase II dashboard with traditional task UI
- Provide both chat and traditional interfaces
- Users choose preferred interaction mode

---

**End of Spec B**
