# 🚀 NoteVault Complete Setup Guide

Your app is ready to deploy! Follow these steps:

## ✅ Step 1: Verify Local Setup

```bash
# Navigate to backend
cd backend

# Verify .env file exists with all variables
cat .env

# You should see:
# SECRET_KEY=014b68f3a3529b62fa122b4fdb2c37527981792eb304f5d72a0d6bdb5ba9f6e2
# MONGO_URI=mongodb+srv://anandjatt689_db_user:iYxGoSsl8xjOmdv1@cluster1.pn1gnfx.mongodb.net/notvault...
# ALLOWED_ORIGINS=https://collage-notesb.vercel.app,http://localhost:3000
# JWT_EXPIRY_HOURS=24
```

## ✅ Step 2: Set Environment Variables in Vercel

### Option A: Automatic (Using Vercel CLI)

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Run setup script
python setup_vercel.py
```

### Option B: Manual (Recommended - Takes 2 minutes)

1. Go to: https://vercel.com/anands-projects-0ed7382e/collage-notesb
2. Click **Settings** tab
3. Click **Environment Variables** (left sidebar)
4. Add each variable:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `014b68f3a3529b62fa122b4fdb2c37527981792eb304f5d72a0d6bdb5ba9f6e2` |
| `MONGO_URI` | `mongodb+srv://anandjatt689_db_user:iYxGoSsl8xjOmdv1@cluster1.pn1gnfx.mongodb.net/notvault?retryWrites=true&w=majority` |
| `ALLOWED_ORIGINS` | `https://collage-notesb.vercel.app,http://localhost:3000` |
| `JWT_EXPIRY_HOURS` | `24` |

5. Click "Save"

## ✅ Step 3: Trigger Redeployment

1. Go to **Deployments** tab
2. Click **Redeploy** on the latest commit
3. OR Vercel auto-redeploys when you push to GitHub

## ✅ Step 4: Verify It Works

**Test in browser console** (Press F12):

```javascript
// Test 1: Health Check
fetch('https://collage-notesb.vercel.app/api/health')
  .then(r => r.json())
  .then(d => console.log('✅ API Health:', d))
  .catch(e => console.log('❌ Error:', e))

// Test 2: Signup (replace with real data)
fetch('https://collage-notesb.vercel.app/api/auth/signup', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'testuser',
    email: 'test@example.com',
    password: 'password123'
  })
})
.then(r => r.json())
.then(d => console.log('✅ Signup Response:', d))
.catch(e => console.log('❌ Error:', e))
```

## 🐛 Troubleshooting

### "Failed to Fetch" Error
- ✅ Verify all 4 environment variables are set in Vercel
- ✅ Wait 2-3 minutes after setting variables
- ✅ Click Redeploy manually
- ✅ Check browser console for CORS errors

### MongoDB Connection Error
- ✅ Verify MONGO_URI is correct
- ✅ Check MongoDB Atlas credentials are correct
- ✅ Ensure IP whitelist allows 0.0.0.0/0

### CORS Error
- ✅ Frontend URL is in `ALLOWED_ORIGINS`
- ✅ Check it includes `https://collage-notesb.vercel.app`

## 📋 Project Structure

```
NoteVault-Complete/
├── backend/              # Flask API
│   ├── app.py           # Main app
│   ├── .env             # Environment variables ✅
│   ├── .env.example     # Template
│   ├── requirements.txt
│   ├── config/
│   │   └── db.py        # MongoDB connection
│   ├── models/          # Data Models
│   ├── routes/          # API endpoints
│   └── middleware/      # Auth middleware
├── frontend/            # Single-page app (React)
│   └── index.html       # All-in-one file
├── vercel.json          # Root deployment config ✅
└── setup_vercel.py      # Setup helper script
```

## 🎯 What's Deployed

- **Backend:** Flask API on Vercel (Python)
- **Frontend:** React SPA on Vercel (Static HTML)
- **Database:** MongoDB Atlas (Cloud)
- **Auth:** JWT tokens (stored in browser localStorage)

## 📚 API Endpoints

```
POST   /api/auth/signup          # Register
POST   /api/auth/login           # Login
GET    /api/auth/me              # Current user (protected)
GET    /api/subjects             # List subjects
POST   /api/subjects             # Create subject
GET    /api/chapters?subject_id  # List chapters
POST   /api/chapters             # Create chapter
GET    /api/notes?chapter_id     # List notes
POST   /api/notes                # Create note
PUT    /api/notes/:id            # Update note
DELETE /api/notes/:id            # Delete note
GET    /api/dashboard/stats      # Dashboard stats
GET    /api/health               # Health check
```

## 🔐 Security Notes

- ⚠️ `.env` file is in `.gitignore` (not committed)
- ⚠️ Environment variables are PRIVATE in Vercel
- ⚠️ MongoDB user credentials must be kept secret
- ⚠️ Rotate `SECRET_KEY` periodically
- ⚠️ Update CORS `ALLOWED_ORIGINS` for production

## ✨ Done!

Your NoteVault is now live! 🎉

- **Frontend:** https://collage-notesb.vercel.app
- **API:** https://collage-notesb.vercel.app/api/health
- **GitHub:** https://github.com/ANAND241-star/Collage-Notes-

**Next:** Share with friends and start taking notes! 📝
