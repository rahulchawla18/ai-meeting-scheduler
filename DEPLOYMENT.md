# Deployment Guide - AI Meeting Scheduler

## Important: Google Calendar OAuth Setup for Production

### Problem:
The current OAuth flow uses `token.pickle` which won't work in production. You need to set up proper OAuth for deployment.

### Solution Options:

## Option A: Use Google Service Account (Recommended for Demo)

1. **Create a Service Account:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
   - Share your calendar with the service account email

2. **Update code to use Service Account:**
   - Store the service account JSON as an environment variable
   - Modify `calendar_service.py` to use service account credentials

## Option B: Keep OAuth but Store Credentials Securely

1. **Generate token.pickle locally**
2. **Convert to base64 and store as environment variable**
3. **Decode in production**

---

## Deployment Steps

### 1. Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Meeting Scheduler"

# Create a new repository on GitHub
# Then push
git remote add origin https://github.com/YOUR_USERNAME/ai-meeting-scheduler.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render (Free)

1. **Sign up:** Go to [render.com](https://render.com) and sign up with GitHub
2. **New Web Service:** Click "New +" → "Web Service"
3. **Connect Repository:** Select your `ai-meeting-scheduler` repo
4. **Configure:**
   - Name: `ai-meeting-scheduler`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:** Add these in Render dashboard:
   - `GROQ_API_KEY`: Your GROQ API key
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`
   - `GROQ_BASE_URL`: `https://api.groq.com/openai/v1`
   - `GOOGLE_CREDENTIALS_JSON`: (Base64 encoded credentials - see below)
   - `TOKEN_PICKLE_BASE64`: (Base64 encoded token - see below)

6. **Deploy:** Click "Create Web Service"

### 3. Encode Credentials for Environment Variables

Run these commands locally:

```bash
# Encode credentials.json
python -c "import base64; print(base64.b64encode(open('credentials.json', 'rb').read()).decode())"

# Encode token.pickle (after authenticating locally)
python -c "import base64; print(base64.b64encode(open('token.pickle', 'rb').read()).decode())"
```

Copy the output and paste into Render environment variables.

---

## Alternative Free Hosting Options

### Option 2: Railway.app
- Free tier: 500 hours/month
- Similar to Render
- [railway.app](https://railway.app)

### Option 3: Fly.io
- Free tier: 3 shared-cpu VMs
- More control
- [fly.io](https://fly.io)

### Option 4: Vercel (Frontend) + Render (Backend)
- Deploy frontend on Vercel (unlimited)
- Backend on Render
- Best performance

---

## Post-Deployment

1. **Test the API:** `https://your-app.onrender.com/`
2. **Update OAuth Redirect URIs:** Add your deployed URL to Google Cloud Console
3. **Share the link:** Your app is live!

---

## Limitations of Free Tier

- **Render:** App sleeps after 15 min of inactivity (cold start ~30s)
- **Railway:** 500 hours/month limit
- **Fly.io:** Limited resources

---

## Recommended: For Production

1. **Use Vercel/Netlify for frontend** (free, fast)
2. **Use Railway/Render for backend** (free tier)
3. **Upgrade to paid tier** for better performance ($7-10/month)

---

## Security Notes

⚠️ **Never commit:**
- `.env` file
- `credentials.json`
- `token.pickle`
- API keys

✅ **Always use:**
- Environment variables
- `.gitignore`
- Secrets management
