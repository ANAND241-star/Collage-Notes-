# 🚀 VERCEL DEPLOYMENT GUIDE

## Step 1: Set Environment Variables in Vercel

1. Go to: https://vercel.com/anands-projects-0ed7382e/collage-notesb
2. Click **Settings** → **Environment Variables**
3. Add these variables:

```
SECRET_KEY=<generate-random-string>
MONGO_URI=<your-mongodb-connection-string>
ALLOWED_ORIGINS=https://collage-notesb.vercel.app,http://localhost:3000
JWT_EXPIRY_HOURS=24
```

### How to Generate Each Variable:

#### SECRET_KEY
Run in terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output as `SECRET_KEY`

#### MONGO_URI
From your MongoDB Atlas:
1. Go to mongodb.com → Clusters
2. Click "Connect" → "Drivers" → Python
3. Copy the connection string
4. Replace `<password>` with your actual password
5. Add `/notvault` at the end
Example: `mongodb+srv://user:password@cluster.mongodb.net/notvault?retryWrites=true&w=majority`

#### ALLOWED_ORIGINS
Same for all:
```
https://collage-notesb.vercel.app,http://localhost:3000
```

#### JWT_EXPIRY_HOURS
```
24
```

## Step 2: Wait for Redeployment

After adding environment variables:
1. Vercel will **automatically redeploy**
2. Or click **"Redeploy"** manually
3. Wait for the build to complete ✓

## Step 3: Test the Connection

Open browser console (F12) and test:
```javascript
fetch('https://collage-notesb.vercel.app/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

You should see:
```json
{"status": "ok", "app": "NoteVault API", "version": "1.0.0"}
```

If this works ✓ then proceed to login/signup.

## Step 4: If Still Getting "Failed to Fetch"

Check:
1. ✅ All 4 environment variables are set
2. ✅ Build completed successfully (check Deployments tab)
3. ✅ Browser console for CORS errors
4. ✅ MongoDB connection string is correct

## Support
If the health check fails, the issue is likely:
- **Missing/wrong environment variables** → Re-add them
- **MongoDB connection failed** → Check credentials
- **CORS blocked** → Check ALLOWED_ORIGINS setting
