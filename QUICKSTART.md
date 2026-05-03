# 🚀 Quick Deployment Checklist

## Step 1: Prepare Credentials (5 minutes)

1. **Authenticate locally first:**
   ```bash
   uvicorn main:app --reload
   # Visit http://localhost:8000 and test scheduling a meeting
   # This will create token.pickle
   ```

2. **Encode credentials:**
   ```bash
   python encode_credentials.py
   ```
   
3. **Copy the output** - You'll need these environment variables

## Step 2: Push to GitHub (2 minutes)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ai-meeting-scheduler.git
git push -u origin main
```

## Step 3: Deploy on Render (5 minutes)

1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `ai-meeting-scheduler`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables:**
   - `GROQ_API_KEY` = (your GROQ API key)
   - `GROQ_MODEL` = `llama-3.3-70b-versatile`
   - `GROQ_BASE_URL` = `https://api.groq.com/openai/v1`
   - `GOOGLE_CREDENTIALS_JSON` = (from encode_credentials.py)
   - `TOKEN_PICKLE_BASE64` = (from encode_credentials.py)

6. Click **"Create Web Service"**

## Step 4: Update Google OAuth (2 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Edit your OAuth 2.0 Client ID
4. Add to **Authorized redirect URIs:**
   - `https://your-app-name.onrender.com/oauth2callback`
5. Save

## Step 5: Test! 🎉

Visit: `https://your-app-name.onrender.com`

---

## ⚡ Alternative: Deploy in 1 Click

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Just add environment variables after deployment!

---

## 💡 Tips

- **First request takes ~30s** (cold start on free tier)
- **App sleeps after 15 min** of inactivity
- **Upgrade to paid tier** ($7/month) for instant response
- **Use custom domain** for professional look

---

## 🆘 Troubleshooting

**Issue:** "Invalid credentials"
- **Fix:** Re-run `encode_credentials.py` and update environment variables

**Issue:** "App not responding"
- **Fix:** Check Render logs for errors

**Issue:** "OAuth error"
- **Fix:** Update redirect URIs in Google Cloud Console

---

## 📊 Free Hosting Comparison

| Platform | Free Tier | Cold Start | Best For |
|----------|-----------|------------|----------|
| **Render** | 750 hrs/mo | ~30s | Full-stack apps |
| **Railway** | 500 hrs/mo | ~10s | Quick deploys |
| **Fly.io** | 3 VMs | ~5s | Performance |
| **Vercel** | Unlimited | Instant | Frontend only |

**Recommendation:** Start with Render, upgrade if needed!
