# AI-meeting-scheduler
An AI-powered meeting scheduler using Google Calendar API and GROQ AI that creates calendar events with Google Meet links and provides smart scheduling features like optimal time suggestions and agenda assistance.

## Prerequisites

1. **GROQ API Key**: Get your API key from [console.groq.com](https://console.groq.com)
2. **Google Calendar API credentials**: Set up OAuth credentials and download `credentials.json`

## Setup

1. Clone the repository
2. Create a `.env` file with your GROQ API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

3. Place your Google Calendar `credentials.json` in the project root

4. Install dependencies:
```bash
pip install -r requirements.lock
# or using uv:
uv sync
```

## Running the Project

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access the API at http://localhost:8000

## API Usage

Send a POST request to `/schedule-meeting`:

```bash
curl -X POST http://localhost:8000/schedule-meeting \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour to discuss project updates"}'
```

The API will:
1. Use GROQ AI to extract meeting details from natural language
2. Create a Google Calendar event with a Meet link
3. Return the event link and parsed details
