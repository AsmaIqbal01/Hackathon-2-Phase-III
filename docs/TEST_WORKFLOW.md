# Browser Testing Workflow for Phase III Todo AI Chatbot

## 🌐 Current Status
- ✅ Backend running: http://127.0.0.1:8000
- ✅ Frontend running: http://localhost:3000
- ✅ Browser opened to: http://localhost:3000

---

## 📋 Test Checklist

### 1️⃣ Initial Page Load
**Expected Behavior:**
- [ ] Browser shows "Initializing..." loading screen
- [ ] Automatically redirects to `/login` page
- [ ] Login form is visible with email and password fields
- [ ] "Register" link is visible
- [ ] Cyberpunk styling (neon blue/purple theme)

**Console Check:**
- Open browser DevTools (F12)
- Go to Console tab
- Look for: `[API] GET /health` or similar logs

---

### 2️⃣ User Registration

**Steps:**
1. Click "Register" link at bottom of login form
2. Enter test credentials:
   - Email: `test@example.com`
   - Password: `Test1234`
3. Click "Register" button

**Expected Behavior:**
- [ ] Loading state: "Creating account..." button text
- [ ] Success toast notification: "Account created successfully"
- [ ] Automatic redirect to `/dashboard`
- [ ] User email displayed in dashboard header
- [ ] Empty task list message: "No tasks yet. Create your first task above!"
- [ ] "Add Task" form visible at top
- [ ] "AI Chat" and "Logout" buttons in header

**Console Logs to Check:**
```javascript
[API] POST /auth/register
[API] Success 201 on /auth/register
[Auth] Registration successful for user: test@example.com
[Dashboard] User authenticated: test@example.com
```

**localStorage Check (DevTools → Application → Local Storage):**
- [ ] `auth_token` exists (JWT token)
- [ ] `user_info` exists (contains email and userId)

---

### 3️⃣ Create Task via Dashboard

**Steps:**
1. In the "Add Task" form at top, enter:
   - Title: `Buy groceries`
2. Click "Add Task" button

**Expected Behavior:**
- [ ] Loading state: "Adding..." button text
- [ ] Success toast: "Task created"
- [ ] New task card appears in list
- [ ] Task shows title: "Buy groceries"
- [ ] Task shows status: "todo" (purple badge)
- [ ] "Complete" and "Delete" buttons visible

**Console Logs:**
```javascript
[API] POST /tasks
[API] Success 201 on /tasks
```

---

### 4️⃣ Test AI Chat Interface

**Steps:**
1. Click "AI Chat" button in header
2. Wait for redirect to `/chat` page

**Expected Behavior:**
- [ ] Chat interface loads
- [ ] User email displayed in header
- [ ] Welcome message: "👋 Welcome to AI Task Assistant"
- [ ] Input field: "Ask me to create, update, or manage your tasks..."
- [ ] "New Chat" and "Logout" buttons in header

**Console Logs:**
```javascript
[Chat] User authenticated: test@example.com
```

**Test AI Chat:**
1. Type in chat: `Create a task called "Finish report"`
2. Press Enter or click "Send"

**Expected Behavior:**
- [ ] User message appears (blue bubble on right)
- [ ] Loading indicator (three bouncing dots)
- [ ] AI response appears (dark bubble on left)
- [ ] AI confirms task creation
- [ ] Success message from AI

**Console Logs:**
```javascript
[Chat] Sending message: Create a task called "Finish report"...
[Chat] Response received successfully
```

---

### 5️⃣ Verify Task Persistence

**Steps:**
1. Navigate back to dashboard (browser back button or type `/dashboard` in URL)
2. Check task list

**Expected Behavior:**
- [ ] Both tasks are visible:
  - "Buy groceries" (created via form)
  - "Finish report" (created via AI chat)
- [ ] Tasks show correct status badges
- [ ] User email still displayed in header

---

### 6️⃣ Complete a Task

**Steps:**
1. Click "Complete" button on "Buy groceries" task

**Expected Behavior:**
- [ ] Loading state on button
- [ ] Success toast: "Task completed"
- [ ] Status badge changes to "completed" (green)
- [ ] Button text changes to "Undo"

**Console Logs:**
```javascript
[API] PATCH /tasks/{id}
[API] Success 200 on /tasks/{id}
```

---

### 7️⃣ Delete a Task

**Steps:**
1. Click "Delete" button on any task
2. Confirmation modal appears

**Expected Behavior:**
- [ ] Modal overlay appears
- [ ] Title: "Delete Task"
- [ ] Description: "Are you sure you want to delete this task? This action cannot be undone."
- [ ] "Delete" and "Cancel" buttons

3. Click "Delete" to confirm

**Expected Behavior:**
- [ ] Success toast: "Task deleted"
- [ ] Task disappears from list with animation
- [ ] Task count updates

**Console Logs:**
```javascript
[API] DELETE /tasks/{id}
[API] Success 204 on /tasks/{id}
```

---

### 8️⃣ Test Logout

**Steps:**
1. Click "Logout" button in dashboard header
2. Confirmation modal appears

**Expected Behavior:**
- [ ] Modal: "Confirm Logout"
- [ ] Description: "Are you sure you want to log out? You will need to sign in again to access your tasks."
- [ ] "Logout" and "Cancel" buttons

3. Click "Logout" to confirm

**Expected Behavior:**
- [ ] Success toast: "Logged out successfully"
- [ ] Redirect to `/login` page
- [ ] Email and password fields are EMPTY
- [ ] No user data in header

**Console Logs:**
```javascript
[Auth] User logged out: test@example.com
```

**localStorage Check:**
- [ ] `auth_token` removed
- [ ] `user_info` removed
- [ ] `phase3_conversation_id` removed

---

### 9️⃣ Test Login (Returning User)

**Steps:**
1. Enter same credentials:
   - Email: `test@example.com`
   - Password: `Test1234`
2. Click "Login" button

**Expected Behavior:**
- [ ] Loading state: "Logging in..." button text
- [ ] Success toast: "Logged in successfully"
- [ ] Redirect to `/dashboard`
- [ ] User email displayed in header
- [ ] **Previous tasks are still visible** (persistence verified!)

**Console Logs:**
```javascript
[API] POST /auth/login
[API] Success 200 on /auth/login
[Auth] Login successful for user: test@example.com
[Dashboard] User authenticated: test@example.com
```

---

### 🔟 Test Multi-User (Data Isolation)

**Steps:**
1. Logout from User 1 (test@example.com)
2. Click "Register" to create User 2
3. Enter different credentials:
   - Email: `user2@example.com`
   - Password: `User2Pass1`
4. Register User 2

**Expected Behavior:**
- [ ] Success: Account created
- [ ] Redirect to dashboard
- [ ] **Empty task list** (User 2 has no tasks)
- [ ] User 2 email displayed: `user2@example.com`

5. Create a task for User 2: `User 2 task`

**Expected Behavior:**
- [ ] Task created successfully
- [ ] Only User 2's task is visible

6. Logout User 2
7. Login as User 1 again (test@example.com)

**Expected Behavior:**
- [ ] User 1's tasks are visible (not User 2's)
- [ ] Data isolation confirmed ✅

---

### 1️⃣1️⃣ Test Error Handling

**Invalid Login:**
1. Logout if logged in
2. Try to login with wrong password:
   - Email: `test@example.com`
   - Password: `WrongPassword`

**Expected Behavior:**
- [ ] Error toast: "Invalid credentials"
- [ ] Red error box above form
- [ ] User stays on login page

**Console Logs:**
```javascript
[API] POST /auth/login
[API] Error 401 on /auth/login: Invalid credentials
```

**Rate Limiting:**
1. Try to login with wrong password 5 times in a row

**Expected Behavior:**
- [ ] After 5 attempts: "Too many login attempts. Try again in X seconds"
- [ ] Login button disabled temporarily
- [ ] `Retry-After` header in response

---

### 1️⃣2️⃣ Test Page Refresh (Session Persistence)

**Steps:**
1. Login successfully
2. Go to dashboard
3. Press F5 or Ctrl+R to refresh page

**Expected Behavior:**
- [ ] Page refreshes
- [ ] User stays logged in (no redirect to login)
- [ ] Tasks still visible
- [ ] User email still in header
- [ ] JWT token still in localStorage

---

### 1️⃣3️⃣ Test Network Tab (API Calls)

**Open DevTools → Network Tab:**

1. Clear network log
2. Login with valid credentials
3. Observe network requests

**Expected API Calls:**
- [ ] `POST /api/auth/login` → Status 200
- [ ] `GET /api/tasks` → Status 200
- [ ] Response headers include `Content-Type: application/json`
- [ ] Request headers include `Authorization: Bearer <token>`

---

## 🐛 Troubleshooting

### Backend Not Responding
```bash
# Check backend process
cd E:/Github/Phase-III/backend
tail -f backend.log

# Restart if needed
pkill -f "uvicorn src.main:app"
uvicorn src.main:app --reload
```

### Frontend Not Responding
```bash
# Check frontend process
cd E:/Github/Phase-III/frontend
tail -f frontend.log

# Restart if needed
pkill -f "next dev"
npm run dev
```

### CORS Errors
- Check backend `.env` has: `CORS_ORIGINS=http://localhost:3000`
- Restart backend after .env changes

### 401 Unauthorized Errors
- Clear localStorage in browser (DevTools → Application → Local Storage → Clear All)
- Try logging in again

---

## ✅ Success Criteria

**All Tests Pass If:**
- ✅ Registration creates new user and logs in
- ✅ Login works with correct credentials
- ✅ Login fails with incorrect credentials
- ✅ Dashboard shows tasks after login
- ✅ Tasks can be created via form and AI chat
- ✅ Tasks can be completed and deleted
- ✅ Logout clears credentials
- ✅ Login restores user's tasks (persistence)
- ✅ Multi-user data isolation works
- ✅ Page refresh maintains session
- ✅ Error messages are friendly and clear
- ✅ Console logs show all operations
- ✅ No errors in browser console (except expected 401 on logout)

---

## 📊 Expected Console Output Summary

**Successful Workflow:**
```javascript
// Initial load
[API] GET /auth/me (may 401 - expected if not logged in)

// Registration
[API] POST /auth/register
[API] Success 201 on /auth/register
[Auth] Registration successful for user: test@example.com

// Dashboard load
[Dashboard] User authenticated: test@example.com
[API] GET /tasks
[API] Success 200 on /tasks

// Create task
[API] POST /tasks
[API] Success 201 on /tasks

// AI Chat
[Chat] User authenticated: test@example.com
[Chat] Sending message: Create a task...
[Chat] Response received successfully

// Logout
[Auth] User logged out: test@example.com
[API] Unauthorized access to /tasks - redirecting to login

// Login
[API] POST /auth/login
[API] Success 200 on /auth/login
[Auth] Login successful for user: test@example.com
```

---

**Ready to test! Browser should be open at http://localhost:3000** 🚀

Follow the checklist above and report any issues you encounter.
