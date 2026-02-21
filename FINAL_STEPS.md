# 🎯 FINAL STEPS - Set Vercel Environment Variables

Follow these steps **EXACTLY** to fix "Failed to Fetch" error:

---

## 📍 STEP 1: Open Vercel Dashboard

Click this link:
```
https://vercel.com/anands-projects-0ed7382e/collage-notesb/settings/environment-variables
```

---

## 🔐 STEP 2: Add Environment Variables

On that page, you'll see "Environment Variables" section.

**Add these 4 variables one by one:**

### Variable 1
**Key:** `SECRET_KEY`
**Value:** 
```
014b68f3a3529b62fa122b4fdb2c37527981792eb304f5d72a0d6bdb5ba9f6e2
```
Click **"Save"**

### Variable 2
**Key:** `MONGO_URI`
**Value:**
```
mongodb+srv://anandjatt689_db_user:iYxGoSsl8xjOmdv1@cluster1.pn1gnfx.mongodb.net/notvault?retryWrites=true&w=majority
```
Click **"Save"**

### Variable 3
**Key:** `ALLOWED_ORIGINS`
**Value:**
```
https://collage-notesb.vercel.app,http://localhost:3000
```
Click **"Save"**

### Variable 4
**Key:** `JWT_EXPIRY_HOURS`
**Value:**
```
24
```
Click **"Save"**

---

## 🚀 STEP 3: Redeploy

1. Go to **"Deployments"** tab
2. Find the latest deployment
3. Click **"Redeploy"** button
4. **Wait 2-3 minutes** for deployment to complete

---

## ✅ STEP 4: Test It Works

Open this in browser console (Press **F12** → Console):

```javascript
fetch('https://collage-notesb.vercel.app/api/health')
  .then(r => r.json())
  .then(d => console.log('✅ Success!', d))
```

You should see:
```
✅ Success! {status: "ok", app: "NoteVault API", version: "1.0.0"}
```

---

## 🎉 Done!

Your app is now fully deployed! 

- **Visit:** https://collage-notesb.vercel.app
- **Try login/signup**
- **Create notes** and they'll be saved to MongoDB!

---

## ❌ Still Getting Error?

Check these:
1. ✅ All 4 variables are EXACTLY as shown above (copy-paste, no typos)
2. ✅ Redeployment finished (check Deployments tab)
3. ✅ Browser cache cleared (Ctrl+Shift+Delete)
4. ✅ MongoDB connection allows all IPs (0.0.0.0/0)

**If still broken:** Share the exact error from browser console and I'll fix it! 🔧
