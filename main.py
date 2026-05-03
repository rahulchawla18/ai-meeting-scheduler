from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from models.event import ScheduleRequest, ExtractedMeeting
from services.groq_service import extract_meeting_from_prompt
from services.calendar_service import create_event
import traceback

app = FastAPI(title="AI Meeting Scheduler")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html"
        )
    except Exception as e:
        print(f"Error loading home page: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to load page", "detail": str(e)}
        )

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "AI Meeting Scheduler is running"}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}

@app.post("/schedule-meeting")
async def schedule_meeting(request: ScheduleRequest):
    try:
        from datetime import timezone
        import pytz
        
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        today_str = now_ist.strftime("%Y-%m-%d %H:%M:%S %Z")
        
        prompt_with_date = f"Today's date is {today_str}. {request.prompt}"
        print("prompt with date...", prompt_with_date)
        # 1) Extract from LLM
        parsed_data = extract_meeting_from_prompt(prompt_with_date)
        meeting_details = ExtractedMeeting(**parsed_data)

        print("meeting details...", meeting_details)

        # 2) Create event via OAuth
        event = create_event(meeting_details)

        return {
            "message": "Meeting scheduled successfully",
            "event_link": event.get("htmlLink"),
            "meeting_details": parsed_data
        }
    except Exception as e:
        # Bubble up concise error
        raise HTTPException(status_code=400, detail=str(e))