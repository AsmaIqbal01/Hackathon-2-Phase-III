# Phase III: Todo AI Chatbot

A full-stack, AI-powered task management application that combines natural language processing with traditional CRUD operations. Phase III builds upon the Phase II Todo app by integrating OpenAI Agents SDK and MCP (Model Context Protocol) tools to provide an intelligent, conversational interface for managing tasks.

![Phase III Architecture](https://img.shields.io/badge/Phase-III-blue) ![AI Powered](https://img.shields.io/badge/AI-Powered-green) ![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 🎯 Project Overview

Phase III introduces AI-driven task management through a stateless backend architecture. Users can interact with their todo list using natural language via an AI chat interface, while maintaining full access to traditional dashboard CRUD operations. The system features multi-user authentication with per-user task persistence, ensuring data isolation and security.

**Key Highlights:**
- **AI-Powered**: Natural language task management using OpenAI Agents SDK
- **Stateless Architecture**: MCP tools handle task operations without server-side state
- **Multi-User Support**: Secure login/logout with JWT authentication and user-scoped tasks
- **Hybrid Interface**: Traditional dashboard + conversational AI chat UI
- **Production Ready**: Comprehensive error handling, logging, and deployment configuration

---

## ✨ Features

### Core Functionality
- 🤖 **AI Chat Interface**: Create, update, and manage tasks using natural language
- 📋 **Dashboard CRUD**: Traditional form-based task management interface
- 🔐 **User Authentication**: Secure registration, login, and logout with JWT tokens
- 💾 **Task Persistence**: Per-user task storage in PostgreSQL database
- 👥 **Multi-User Support**: Complete data isolation between users
- 🎨 **Cyberpunk UI**: Modern, responsive design with Tailwind CSS

### Technical Features
- ⚡ **Stateless Backend**: No server-side session management
- 🛠️ **MCP Tools Integration**: Task operations via Model Context Protocol
- 🔒 **Rate Limiting**: Protection against brute-force login attempts
- 📊 **Comprehensive Logging**: Debug logging without sensitive data exposure
- ✅ **Confirmation Prompts**: AI-driven confirmations for destructive actions
- 🔄 **Conversation History**: Persistent chat context per user

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.1.6 | React framework with App Router |
| **React** | 19.2.4 | UI component library |
| **TypeScript** | 5.9.3 | Type-safe JavaScript |
| **Tailwind CSS** | 4.1.18 | Utility-first CSS framework |
| **Framer Motion** | 12.31.0 | Animation library |
| **React Hot Toast** | 2.6.0 | Toast notifications |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | Modern Python web framework |
| **Python** | 3.13+ | Programming language |
| **OpenAI Agents SDK** | Latest | AI agent orchestration |
| **MCP SDK** | Latest | Model Context Protocol tools |
| **SQLModel** | Latest | SQL ORM with Pydantic validation |
| **Neon PostgreSQL** | Latest | Production database |
| **SQLite** | 3.x | Development database |
| **Bcrypt** | Latest | Password hashing |
| **PyJWT** | Latest | JWT token management |

---

## 🚀 Setup Instructions

### Prerequisites
- **Python**: 3.13 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **OpenAI API Key**: Required for AI features

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your values:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=sk-proj-...

   # Database Configuration
   DATABASE_URL=sqlite:///./todo.db  # Development
   # DATABASE_URL=postgresql://user:pass@host/db  # Production

   # JWT Configuration
   JWT_SECRET=your-secret-key-here  # Generate: openssl rand -hex 32
   JWT_ALGORITHM=HS256
   JWT_ACCESS_EXPIRE_MINUTES=30
   JWT_REFRESH_EXPIRE_DAYS=7

   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

   # Application Settings
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

5. **Run the backend server:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend accessible at: **http://localhost:8000**

   API Documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   Create a `.env.local` file in the `frontend/` directory:
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and set your backend API URL:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Run the Development Server:**
   ```bash
   npm run dev
   ```

   The application will be available at [http://localhost:3000](http://localhost:3000).

### Verify Installation

1. Visit http://localhost:3000 → Should redirect to login page
2. Register a new account
3. Create a task via dashboard or AI chat
4. Verify task persistence after logout/login

---

## 📖 Usage

### User Authentication

**Registration:**
1. Navigate to http://localhost:3000
2. Click "Register" link
3. Enter email and password (min 8 characters, must include letter and number)
4. Automatically logged in after registration

**Login:**
1. Enter email and password
2. Click "Login"
3. Redirected to dashboard with your tasks

**Logout:**
1. Click "Logout" button in dashboard or chat
2. Confirm logout action
3. Redirected to login page (tasks preserved in database)

### Task Management

#### Dashboard (Traditional Interface)
- **Create Task**: Enter title in input field, click "Add Task"
- **Complete Task**: Click "Complete" button on task card
- **Undo Completion**: Click "Undo" on completed task
- **Delete Task**: Click "Delete" → Confirm in modal

#### AI Chat Interface
Navigate to chat via "AI Chat" button in dashboard.

**Example Commands:**
```
User: Create a task called "Buy groceries"
AI: ✓ Task created: Buy groceries

User: Show all my tasks
AI: You have 3 tasks:
    1. Buy groceries (todo)
    2. Finish report (in-progress)
    3. Call dentist (completed)

User: Mark "Buy groceries" as completed
AI: Confirm: Mark "Buy groceries" as completed?
User: [Confirms]
AI: ✓ Task completed: Buy groceries

User: Delete all completed tasks
AI: Confirm: Delete 1 completed task?
User: [Confirms]
AI: ✓ Deleted 1 task
```

### Multi-User Workflow

**User Switching:**
1. User A logs in → Creates tasks → Logs out
2. User B logs in → Sees empty task list (data isolation)
3. User A logs back in → Sees their original tasks (persistence)

---

## 📁 Project Structure

```
Phase-III/
├── backend/                      # FastAPI backend server
│   ├── src/
│   │   ├── agents/              # OpenAI agent implementations
│   │   │   ├── master_agent.py # Main orchestrator
│   │   │   ├── task_agent.py   # Task operations handler
│   │   │   └── confirmation_agent.py
│   │   ├── api/
│   │   │   ├── routes/         # API endpoints
│   │   │   │   ├── auth.py     # Authentication routes
│   │   │   │   ├── tasks.py    # Task CRUD routes
│   │   │   │   └── chat.py     # AI chat routes
│   │   │   └── deps.py         # Dependency injection
│   │   ├── models/             # SQLModel database models
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── conversation.py
│   │   │   └── message.py
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── task_service.py
│   │   │   └── conversation_service.py
│   │   ├── mcp/                # MCP server implementation
│   │   │   ├── server.py       # MCP tool definitions
│   │   │   └── context.py      # Request context
│   │   ├── utils/              # Utilities
│   │   │   ├── security.py     # JWT, hashing, validation
│   │   │   └── rate_limiter.py
│   │   ├── database.py         # Database connection
│   │   ├── config.py           # Settings management
│   │   └── main.py             # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment template
│
├── frontend/                    # Next.js frontend application
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home redirect
│   │   ├── login/              # Login page
│   │   ├── register/           # Registration page
│   │   ├── dashboard/          # Task dashboard
│   │   └── chat/               # AI chat interface
│   ├── components/
│   │   ├── TaskForm.tsx        # Task creation form
│   │   ├── TaskItem.tsx        # Task card component
│   │   ├── TaskList.tsx        # Task list container
│   │   ├── chat/               # Chat components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ConfirmationModal.tsx
│   │   └── ui/                 # Reusable UI components
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Auth helpers
│   │   ├── chatApi.ts          # Chat API client
│   │   └── types.ts            # TypeScript types
│   ├── package.json            # Node dependencies
│   └── .env.example           # Environment template
│
├── specs/                       # Feature specifications
│   └── phase-iii/
│       ├── spec.md             # Requirements
│       ├── plan.md             # Architecture
│       └── tasks.md            # Implementation tasks
│
├── history/                     # Development history
│   ├── prompts/                # Prompt history records (PHR)
│   └── adr/                    # Architecture decision records
│
├── .specify/                    # SpecKit configuration
│   ├── memory/
│   │   └── constitution.md     # Project principles
│   └── templates/              # Document templates
│
├── IMPLEMENTATION_SUMMARY.md    # Complete feature documentation
└── README.md                    # This file
```

---

## 🚀 Key Improvements from Phase II

### 1. AI Integration
- **Phase II**: Manual CRUD operations via forms
- **Phase III**: Natural language task management with OpenAI Agents SDK
- **Benefit**: Intuitive, conversational interface for task management

### 2. Stateless Architecture
- **Phase II**: Traditional session-based state management
- **Phase III**: Stateless backend with MCP tools for task operations
- **Benefit**: Better scalability, easier deployment, no session management overhead

### 3. Enhanced Authentication
- **Phase II**: Basic authentication
- **Phase III**: JWT with refresh tokens, rate limiting, secure logout
- **Benefit**: Production-grade security with token rotation and brute-force protection

### 4. Multi-User Support
- **Phase II**: Single-user application
- **Phase III**: Complete multi-user support with data isolation
- **Benefit**: Multiple users can independently manage their tasks

### 5. Conversation History
- **Phase II**: N/A (no AI chat)
- **Phase III**: Persistent conversation context per user
- **Benefit**: Contextual AI responses, better user experience

### 6. Error Handling & Logging
- **Phase II**: Basic error messages
- **Phase III**: Comprehensive logging, friendly error messages, console debugging
- **Benefit**: Better debugging, improved user experience, production-ready monitoring

### 7. Confirmation System
- **Phase II**: Immediate destructive actions
- **Phase III**: AI-driven confirmation prompts for delete operations
- **Benefit**: Prevents accidental data loss, better UX

### 8. Modern UI/UX
- **Phase II**: Basic styling
- **Phase III**: Cyberpunk theme, animations, responsive design, toast notifications
- **Benefit**: Professional appearance, better mobile experience

---

## 🌐 API Endpoints

### Authentication
```
POST   /api/auth/register      # Create new user account
POST   /api/auth/login         # Authenticate and receive tokens
POST   /api/auth/logout        # Revoke refresh tokens
POST   /api/auth/refresh       # Refresh access token
GET    /api/auth/me            # Get current user profile
```

### Tasks (RESTful)
```
GET    /api/tasks              # List all user's tasks (with filters)
POST   /api/tasks              # Create new task
GET    /api/tasks/{id}         # Get single task
PATCH  /api/tasks/{id}         # Update task (partial)
DELETE /api/tasks/{id}         # Delete task
```

### AI Chat
```
POST   /api/chat               # Send chat message to AI agent
GET    /api/chat/conversations/{id}/messages  # Load conversation history
DELETE /api/chat/conversations/{id}           # Delete conversation
```

### Documentation
```
GET    /docs                   # Swagger UI (interactive API docs)
GET    /redoc                  # ReDoc (alternative API docs)
GET    /openapi.json           # OpenAPI schema
```

---

## 🔒 Security Features

- **Password Hashing**: Bcrypt with salt rounds
- **JWT Authentication**: HS256 algorithm with 30-minute access tokens
- **Refresh Token Rotation**: One-time use refresh tokens with 7-day expiry
- **Rate Limiting**: 5 login attempts per 15 minutes
- **CORS Protection**: Configurable allowed origins
- **SQL Injection Prevention**: SQLModel ORM with parameterized queries
- **Input Validation**: Pydantic schemas for all requests
- **Secure Logout**: Token revocation on logout

---

## 🧪 Testing

### Manual Testing Checklist

**Authentication:**
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Logout and verify token cleared
- [ ] Rate limiting after 5 failed attempts

**Task Operations:**
- [ ] Create task via dashboard
- [ ] Create task via AI chat
- [ ] Update task status
- [ ] Delete task with confirmation
- [ ] Filter tasks by status

**Multi-User:**
- [ ] User A creates tasks
- [ ] Logout User A
- [ ] User B logs in, sees empty list
- [ ] User A logs back in, sees original tasks

**UI/UX:**
- [ ] Responsive design on mobile
- [ ] Toast notifications for all actions
- [ ] Loading states during async operations
- [ ] Error messages are user-friendly

### Automated Testing (Future)
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📦 Deployment

### Backend (Railway / Heroku)

1. **Set environment variables:**
   ```env
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   OPENAI_API_KEY=sk-proj-...
   JWT_SECRET=<generated-secret>
   CORS_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```

2. **Deploy via Railway:**
   ```bash
   railway login
   railway link
   railway up
   ```

3. **Or via Heroku:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Frontend (Vercel / Netlify)

1. **Set environment variable:**
   ```env
   NEXT_PUBLIC_API_BASE_URL=https://your-backend.railway.app
   ```

2. **Deploy via Vercel:**
   ```bash
   vercel login
   vercel --prod
   ```

3. **Or via GitHub integration:**
   - Push to GitHub
   - Connect repository in Vercel dashboard
   - Configure environment variables
   - Deploy automatically

### Database Migration

**From SQLite to PostgreSQL:**
```bash
# Export data from SQLite
sqlite3 todo.db .dump > backup.sql

# Import to PostgreSQL (adjust syntax)
psql $DATABASE_URL < backup_adjusted.sql
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Ensure you're in backend directory
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn src.main:app --reload
```

**Problem**: Database connection error
```bash
# Solution: Check DATABASE_URL in .env
# For SQLite: sqlite:///./todo.db (relative path)
# For PostgreSQL: postgresql://user:pass@host/db
```

**Problem**: OpenAI API error
```bash
# Solution: Verify OPENAI_API_KEY in .env
# Check API key is active at https://platform.openai.com/api-keys
```

### Frontend Issues

**Problem**: `API_BASE_URL is undefined`
```bash
# Solution: Create .env.local with:
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

**Problem**: CORS error in browser
```bash
# Solution: Add frontend URL to backend CORS_ORIGINS
# In backend/.env:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Problem**: 401 Unauthorized errors
```bash
# Solution: Clear localStorage and login again
# In browser console:
localStorage.clear()
location.reload()
```

---

## 🤝 Contributing

This is an educational project for learning full-stack development with AI integration. Contributions are welcome!

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style
- **Backend**: Follow PEP 8, use type hints
- **Frontend**: Follow Airbnb style guide, use TypeScript
- **Commits**: Use conventional commits (feat, fix, docs, etc.)

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Phase III Todo AI Chatbot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

For questions, issues, or feature requests:
- **Issues**: [GitHub Issues](https://github.com/your-repo/phase-iii/issues)
- **Documentation**: See `/specs/phase-iii/` directory
- **API Docs**: http://localhost:8000/docs (when running locally)

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [OpenAI Agents SDK](https://github.com/openai/swarm)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

**Built with ❤️ using OpenAI, FastAPI, and Next.js**

*Phase III represents the evolution from traditional CRUD applications to AI-powered, conversational interfaces while maintaining robust architecture and production-ready code.*
