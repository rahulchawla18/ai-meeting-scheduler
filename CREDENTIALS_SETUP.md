# Missing credentials.json

You need to add your Google OAuth credentials file.

## Steps to get credentials.json:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API** and **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Download the JSON file
7. Rename it to `credentials.json`
8. Place it in the project root directory

## After adding credentials.json:

Run the app locally:
```bash
uvicorn main:app --reload
```

Visit http://localhost:8000 and schedule a test meeting. This will:
- Open a browser for Google OAuth authentication
- Create `token.pickle` file
- Now you can use the app!

## For Deployment:

After authenticating locally, run:
```bash
python encode_credentials.py
```

This will give you the environment variables needed for deployment.
