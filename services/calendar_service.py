from __future__ import annotations
import os
import pickle
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, List
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send"
]
TOKEN_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "credentials.json"  # OAuth client JSON


def get_services():
    """Return both Calendar and Gmail service objects using OAuth 2.0."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, prompt="consent")

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    calendar_service = build("calendar", "v3", credentials=creds)
    gmail_service = build("gmail", "v1", credentials=creds)
    return calendar_service, gmail_service


def _parse_iso(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(dt_str)
    except Exception as e:
        raise ValueError(f"Invalid ISO datetime: {dt_str}. Error: {e}")


def _maybe_add_timezone(dt: datetime) -> Dict[str, str]:
    base = {"dateTime": dt.isoformat()}
    if dt.tzinfo is None:
        base["timeZone"] = "Asia/Kolkata"
    return base


def _send_email(gmail_service, to_email: str, subject: str, body_text: str):
    """Send an email using Gmail API."""
    message = MIMEText(body_text)
    message["to"] = to_email
    message["from"] = "me"  # "me" means authenticated user
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    gmail_service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()


def create_event(details: Any) -> Dict[str, Any]:
    """Create a calendar event and send email notifications."""
    if isinstance(details, dict):
        title = details.get("title", "")
        start_time = details.get("start_time")
        duration_minutes = details.get("duration_minutes", 30)
        participants: List[str] = details.get("participants", [])
        agenda = details.get("agenda", "")
    else:
        title = getattr(details, "title", "")
        start_time = getattr(details, "start_time", None)
        duration_minutes = getattr(details, "duration_minutes", 30)
        participants = list(getattr(details, "participants", []))
        agenda = getattr(details, "agenda", "")

    if not start_time:
        raise ValueError("start_time is required")

    start_dt = _parse_iso(start_time)
    end_dt = start_dt + timedelta(minutes=int(duration_minutes))

    event_body = {
        "summary": title or "Meeting",
        "description": agenda or "",
        "start": _maybe_add_timezone(start_dt),
        "end": _maybe_add_timezone(end_dt),
    }

    if participants:
        event_body["attendees"] = [{"email": e} for e in participants]

    try:
        calendar_service, gmail_service = get_services()

        created_event = (
            calendar_service.events()
            .insert(calendarId="primary", body=event_body, sendUpdates="all")
            .execute()
        )

        # Send email notifications to all participants
        for email in participants:
            _send_email(
                gmail_service,
                to_email=email,
                subject=f"Invitation: {title}",
                body_text=f"You have been invited to '{title}'\n"
                          f"Agenda: {agenda}\n"
                          f"Start: {start_dt}\n"
                          f"End: {end_dt}\n"
                          f"Event Link: {created_event.get('htmlLink')}"
            )

        return created_event

    except HttpError as he:
        raise RuntimeError(f"Google Calendar API error: {he}")
