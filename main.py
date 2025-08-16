from datetime import datetime
from fastapi import FastAPI, HTTPException
from models.event import ScheduleRequest, ExtractedMeeting
from services.ollama_service import extract_meeting_from_prompt
from services.calendar_service import create_event

app = FastAPI(title="AI Meeting Scheduler")

@app.post("/schedule-meeting")
async def schedule_meeting(request: ScheduleRequest):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
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