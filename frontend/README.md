# Todo App Frontend

**Phase II Full-Stack Web Application Frontend**

This is the frontend web application for the Evolution of Todo Phase II project, built with Next.js 16+, TypeScript, and Tailwind CSS.

---

## Overview

A minimal Next.js frontend demonstrating secure full-stack integration with the FastAPI backend. This application allows users to register, login, and manage their personal tasks with complete data isolation.

## Features

- User authentication (register/login)
- JWT-based authorization
- Task CRUD operations (Create, Read, Update, Delete)
- Task status toggling (todo ↔ completed)
- Responsive UI with Tailwind CSS
- Secure token storage
- User data isolation

---

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API Client**: Native Fetch API
- **State Management**: React Hooks (useState, useEffect)
- **Authentication**: JWT tokens stored in localStorage

---

## Prerequisites

- Node.js 18+ and npm
- Running backend API (see `../backend/README.md`)

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Redirect logic (/ → /login or /dashboard)
│   ├── login/page.tsx       # Login page
│   ├── register/page.tsx    # Registration page
│   └── dashboard/page.tsx   # Task dashboard (protected)
├── components/
│   ├── TaskList.tsx         # Task list with loading/error/empty states
│   ├── TaskItem.tsx         # Individual task with toggle/delete actions
│   └── TaskForm.tsx         # Create task form
├── lib/
│   ├── types.ts             # TypeScript type definitions
│   ├── auth.ts              # Token storage helpers
│   └── api.ts               # API client with JWT injection
├── .env.example             # Environment variable template
└── README.md                # This file
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
cp .env.example .env.local
```

Edit `.env.local` and set your backend API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

---

## Usage

### Register a New Account

1. Navigate to [http://localhost:3000](http://localhost:3000)
2. Click "Register"
3. Enter email and password
4. Submit to create account and auto-login

### Login

1. Navigate to [http://localhost:3000/login](http://localhost:3000/login)
2. Enter credentials
3. Submit to login and redirect to dashboard

### Manage Tasks

**Create Task:**
- Enter task title in the input field
- Click "Add Task"

**Toggle Status:**
- Click "Complete" to mark as completed
- Click "Undo" to mark as todo

**Delete Task:**
- Click "Delete" button
- Confirm deletion

**Logout:**
- Click "Logout" button in dashboard header

---

## API Integration

All API requests are handled by the centralized `apiClient` in `lib/api.ts`:

- Automatically injects `Authorization: Bearer <token>` header
- Handles 401 responses by clearing token and redirecting to login
- Parses error responses and throws user-friendly errors

### Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login with credentials |
| GET | `/tasks` | Fetch user's tasks |
| POST | `/tasks` | Create new task |
| PATCH | `/tasks/{id}` | Update task (toggle status) |
| DELETE | `/tasks/{id}` | Delete task |

---

## Security

- JWT tokens stored in `localStorage` (acceptable for hackathon scope)
- All task API requests require authentication
- Backend enforces user-scoped data access
- 401 responses automatically clear token and redirect to login
- No secrets committed to repository (see `.gitignore`)

---

## Build for Production

```bash
npm run build
npm start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api` |

## Troubleshooting

### "Unauthorized" errors

- Ensure backend is running
- Check that `NEXT_PUBLIC_API_URL` points to correct backend
- Try logging out and logging back in

### Tasks not appearing

- Verify user is logged in
- Check browser console for errors
- Ensure backend database is running

### Registration fails

- Check if email already exists
- Verify backend validation rules
- Check network tab for detailed error

## Development

### Running the Development Server

```bash
npm run dev
```

### Linting

```bash
npm run lint
```

---

## License

This project is for educational and hackathon purposes.

---

**Next Steps**: Refer to `../backend/README.md` to set up the backend API.
