from pydantic import BaseModel, EmailStr
from typing import List

class ScheduleRequest(BaseModel):
    prompt: str

class ExtractedMeeting(BaseModel):
    title: str
    participants: List[EmailStr] = []
    start_time: str  # ISO8601 format
    duration_minutes: int
    agenda: str = ""