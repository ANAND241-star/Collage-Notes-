# 🗂️ NoteVault — Complete Setup Guide
> Full-stack College Notes App · Flask + MongoDB + HTML Frontend

---

## 📁 Project Structure

```
NoteVault-Complete/
├── 📄 README.md                ← You are here
│
├── 🌐 frontend/
│   └── index.html              ← The entire frontend (open in browser)
│
└── 🐍 backend/
    ├── app.py                  ← Flask entry point
    ├── requirements.txt        ← Python dependencies
    ├── .env.example            ← Environment variables template
    ├── config/
    │   └── db.py               ← MongoDB connection
    ├── middleware/
    │   └── auth.py             ← JWT authentication
    ├── models/
    │   ├── user.py             ← User model (bcrypt + JWT)
    │   └── note.py             ← Note/Subject/Chapter models
    └── routes/
        ├── auth.py             ← POST /api/auth/signup, /login
        ├── subjects.py         ← CRUD /api/subjects
        ├── chapters.py         ← CRUD /api/chapters
        ├── notes.py            ← CRUD /api/notes + search
        └── dashboard.py        ← GET /api/dashboard/stats
```

---

## ✅ Prerequisites — Install These First

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | https://python.org |
| MongoDB | 6.0+ | https://www.mongodb.com/try/download/community |
| Git (optional) | any | https://git-scm.com |

> 💡 **No Node.js needed** — the frontend is a single HTML file!

---

## 🚀 STEP-BY-STEP SETUP

---

### STEP 1 — Start MongoDB

**Windows:**
```
1. Open Services (Win + R → type "services.msc")
2. Find "MongoDB" → Right click → Start
```
OR run in terminal:
```bash
net start MongoDB
```

**Mac:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

**Verify MongoDB is running:**
```bash
mongosh
# You should see the MongoDB shell prompt
# Type: exit  to quit
```

> ☁️ **OR use MongoDB Atlas (Free Cloud):**
> 1. Go to https://www.mongodb.com/atlas
> 2. Create free account → Create Cluster (free tier)
> 3. Get connection string → paste into .env as MONGO_URI

---

### STEP 2 — Setup the Backend

Open a terminal and run these commands:

```bash
# Navigate into the backend folder
cd NoteVault-Complete/backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

You should see packages installing including Flask, PyMongo, bcrypt, PyJWT, etc.

---

### STEP 3 — Configure Environment Variables

```bash
# Copy the example file to create your .env
cp .env.example .env
```

Now open `.env` in any text editor and configure:

```env
# Flask
FLASK_DEBUG=true
PORT=5000

# IMPORTANT: Change this to a long random string in production!
SECRET_KEY=notvault-my-secret-key-change-this

# MongoDB (choose one):
# Local MongoDB:
MONGO_URI=mongodb://localhost:27017/notvault

# MongoDB Atlas (cloud) - replace with your connection string:
# MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/notvault

# JWT token lifetime
JWT_EXPIRY_HOURS=24

# CORS — keep * for development, change to your URL in production
ALLOWED_ORIGINS=*
```

---

### STEP 4 — Start the Backend Server

```bash
# Make sure you're in the backend folder with venv activated
python app.py
```

✅ **You should see:**
```
✅  MongoDB connected → notvault
✅  MongoDB indexes created
🚀  NoteVault API running on http://localhost:5000
```

**Test it works:**
Open your browser and go to:
```
http://localhost:5000/api/health
```
You should see: `{"status": "ok", "app": "NoteVault API", "version": "1.0.0"}`

---

### STEP 5 — Open the Frontend

Open a **new terminal** (keep the backend running in the first one):

```bash
# Navigate to the frontend folder
cd NoteVault-Complete/frontend

# Start a local web server
python -m http.server 3000
```

Then open your browser and go to:
```
http://localhost:3000/index.html
```

> ⚠️ **Do NOT open the HTML file by double-clicking it!**
> That uses `file://` which causes CORS errors.
> Always use `http://localhost:3000` instead.

---

### STEP 6 — Connect Frontend to Backend

Open `frontend/index.html` in a text editor.

Find this line near the top of the JavaScript (around line 360):

```javascript
// Currently using localStorage — to connect to backend, add:
const API_URL = "http://localhost:5000/api";
```

The frontend works **standalone with localStorage** right out of the box.

To **connect it to the Flask backend**, follow the Connection Guide
that came with this package (NoteVault_Connection_Guide.html).

---

## 🧪 Test the Full Backend with curl

```bash
# 1. Health check
curl http://localhost:5000/api/health

# 2. Register an account
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","email":"student@test.com","password":"pass1234"}'

# 3. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"pass1234"}'

# Copy the token from the response, then:

# 4. Create a subject (replace TOKEN below)
curl -X POST http://localhost:5000/api/subjects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Physics","color":"#6C63FF","icon":"⚗️"}'

# 5. Dashboard stats
curl http://localhost:5000/api/dashboard/stats \
  -H "Authorization: Bearer TOKEN"
```

---

## 📡 Full API Reference

### Auth (No token needed)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/signup | Register new user |
| POST | /api/auth/login | Login, get JWT token |
| GET | /api/auth/me 🔒 | Get current user |
| PUT | /api/auth/me 🔒 | Update profile |
| POST | /api/auth/logout 🔒 | Logout |

### Notes (Token required 🔒)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/subjects | List all subjects |
| POST | /api/subjects | Create subject |
| PUT | /api/subjects/:id | Update subject |
| DELETE | /api/subjects/:id | Delete (cascade) |
| GET | /api/chapters?subject_id= | List chapters |
| POST | /api/chapters | Create chapter |
| DELETE | /api/chapters/:id | Delete (cascade) |
| GET | /api/notes?chapter_id= | List notes |
| GET | /api/notes/search?q= | Full-text search |
| POST | /api/notes | Create note |
| PUT | /api/notes/:id | Update/save note |
| DELETE | /api/notes/:id | Delete note |
| GET | /api/dashboard/stats | All dashboard data |

---

## 🔧 Common Problems & Fixes

### ❌ "MongoDB connection failed"
- Make sure MongoDB is running (Step 1)
- Check MONGO_URI in your .env file
- For Atlas: whitelist your IP in Atlas → Network Access

### ❌ CORS error in browser
- Make sure Flask is running on port 5000
- Set `ALLOWED_ORIGINS=*` in .env for development
- Always open frontend via `http://localhost:3000`, not file://

### ❌ 401 Unauthorized on every request
- You need to be logged in to use protected routes
- The token expires after 24 hours (set in JWT_EXPIRY_HOURS)
- Check that SECRET_KEY hasn't changed between restarts

### ❌ "ModuleNotFoundError"
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

### ❌ Port 5000 already in use
- Change PORT=5001 in .env
- Or kill the process: `lsof -ti:5000 | xargs kill` (Mac/Linux)

---

## ☁️ Deploy to the Cloud (Free)

### Database → MongoDB Atlas
1. mongodb.com/atlas → Create free cluster
2. Database Access → Add user with password
3. Network Access → Add IP (0.0.0.0/0 for all)
4. Connect → Get connection string

### Backend → Render.com (Free)
1. Push backend folder to GitHub
2. render.com → New Web Service → Connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn -w 4 "app:create_app()"`
5. Add Environment Variables from your .env

### Frontend → Netlify (Free)
1. netlify.com/drop → Drag your frontend folder
2. Update API_URL in index.html to your Render URL
3. Done! 🎉

---

## 🛡️ Security Features Built In

- ✅ Passwords hashed with **bcrypt** (never stored plain)
- ✅ **JWT tokens** with configurable expiry
- ✅ All data queries filtered by **user_id** (users can't see each other's notes)
- ✅ Input validation on all endpoints
- ✅ CORS restricted to allowed origins
- ✅ Cascade deletes keep database clean

---

## 🌟 Frontend Features (v5)

- 📚 Subject → Chapter → Note hierarchy
- 🏠 Dashboard with stats, charts, heatmap
- 🖼️ Image & Video upload (drag & drop or click)
- 📄 Download note as **PDF**
- 📝 Download note as **Word (.doc)**
- 🌙 Dark / Light theme toggle
- 💾 Auto-save every 2 seconds
- 🔍 Search across all notes
- 🏷️ Tags system
- ⌨️ Keyboard shortcuts (Ctrl+S, Ctrl+N, Ctrl+B, Ctrl+I)
- 📊 Word & character count
- 🔥 Activity heatmap & study streak

---

*Built with Flask · MongoDB · React (CDN) · No build step required*
