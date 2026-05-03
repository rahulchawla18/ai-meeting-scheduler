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
    try:
        creds = None
        
        # Check if running in production (environment variables set)
        import os
        credentials_base64 = os.getenv('GOOGLE_CREDENTIALS_JSON')
        token_base64 = os.getenv('TOKEN_PICKLE_BASE64')
        
        if token_base64:
            # Production mode: decode from environment variables
            import base64
            
            # Decode and load token
            token_data = base64.b64decode(token_base64)
            creds = pickle.loads(token_data)
            
            # If credentials expired, try to refresh
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(GoogleRequest())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    raise ValueError("OAuth token expired. Please re-authenticate and update TOKEN_PICKLE_BASE64 environment variable.")
        else:
            # Local development mode: use files
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise ValueError(f"Missing {CLIENT_SECRETS_FILE}. Please add your Google OAuth credentials file.")
            
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
    except Exception as e:
        raise ValueError(f"Error initializing Google services: {e}")


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
    """Send an HTML email using Gmail API."""
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    message = MIMEMultipart('alternative')
    message["to"] = to_email
    message["from"] = "me"
    message["subject"] = subject
    
    # Plain text version
    text_part = MIMEText(body_text, 'plain')
    
    # HTML version with enhanced design
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 20px;
                line-height: 1.6;
            }}
            .email-wrapper {{ 
                max-width: 650px; 
                margin: 0 auto; 
                background: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 50px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: pulse 15s ease-in-out infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); opacity: 0.5; }}
                50% {{ transform: scale(1.1); opacity: 0.8; }}
            }}
            .header-icon {{ 
                font-size: 64px;
                margin-bottom: 15px;
                display: inline-block;
                animation: bounce 2s ease-in-out infinite;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            .header h1 {{ 
                color: white;
                font-size: 32px;
                font-weight: 700;
                margin: 0;
                position: relative;
                z-index: 1;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }}
            .header p {{
                color: rgba(255,255,255,0.9);
                font-size: 16px;
                margin-top: 10px;
                position: relative;
                z-index: 1;
            }}
            .content {{ 
                padding: 50px 40px;
                background: #ffffff;
            }}
            .meeting-title {{
                font-size: 28px;
                color: #2d3748;
                font-weight: 700;
                margin-bottom: 30px;
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 3px solid #667eea;
            }}
            .info-card {{
                margin: 25px 0;
                padding: 25px;
                background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
                border-radius: 15px;
                border-left: 5px solid #667eea;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .info-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
            }}
            .info-label {{
                font-size: 14px;
                font-weight: 700;
                color: #667eea;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .info-value {{
                font-size: 18px;
                color: #2d3748;
                font-weight: 500;
                line-height: 1.6;
            }}
            .button-container {{
                text-align: center;
                margin: 40px 0;
                padding: 30px 0;
                background: linear-gradient(to bottom, transparent, #f7fafc, transparent);
            }}
            .button {{
                display: inline-block;
                padding: 16px 40px;
                margin: 10px 8px;
                font-size: 16px;
                font-weight: 700;
                text-decoration: none;
                border-radius: 50px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .meet-button {{
                background: linear-gradient(135deg, #34a853 0%, #2d8e47 100%);
                color: white;
            }}
            .meet-button:hover {{
                background: linear-gradient(135deg, #2d8e47 0%, #34a853 100%);
                box-shadow: 0 6px 25px rgba(52, 168, 83, 0.4);
                transform: translateY(-3px);
            }}
            .calendar-button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .calendar-button:hover {{
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
                transform: translateY(-3px);
            }}
            .tips-section {{
                margin-top: 40px;
                padding: 30px;
                background: linear-gradient(135deg, #e8f4f8 0%, #d4e9f2 100%);
                border-radius: 15px;
                border: 2px dashed #667eea;
            }}
            .tips-title {{
                font-size: 18px;
                font-weight: 700;
                color: #2d3748;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .tips-list {{
                list-style: none;
                padding: 0;
            }}
            .tips-list li {{
                padding: 10px 0;
                color: #4a5568;
                font-size: 15px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .tips-list li::before {{
                content: '✓';
                display: inline-block;
                width: 24px;
                height: 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 50%;
                text-align: center;
                line-height: 24px;
                font-weight: bold;
                flex-shrink: 0;
            }}
            .footer {{
                text-align: center;
                padding: 30px 40px;
                background: linear-gradient(to bottom, #f7fafc, #edf2f7);
                color: #718096;
                font-size: 13px;
                border-top: 1px solid #e2e8f0;
            }}
            .footer-logo {{
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .divider {{
                height: 3px;
                background: linear-gradient(to right, transparent, #667eea, transparent);
                margin: 30px 0;
                border-radius: 2px;
            }}
            @media only screen and (max-width: 600px) {{
                .content {{ padding: 30px 20px; }}
                .header {{ padding: 40px 20px; }}
                .meeting-title {{ font-size: 22px; }}
                .button {{ padding: 14px 30px; font-size: 14px; margin: 8px 4px; }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <div class="header-icon">✉️</div>
                <h1>Meeting Invitation</h1>
                <p>You've been invited to join an important meeting</p>
            </div>
            <div class="content">
                {body_text}
            </div>
            <div class="footer">
                <div class="footer-logo">🤖</div>
                <p><strong>AI Meeting Scheduler</strong></p>
                <p style="margin-top: 8px;">Powered by GROQ AI & Google Calendar</p>
                <p style="margin-top: 15px; font-size: 11px; color: #a0aec0;">This is an automated invitation. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    html_part = MIMEText(html_content, 'html')
    
    message.attach(text_part)
    message.attach(html_part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    gmail_service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()


def create_event(details: Any) -> Dict[str, Any]:
    """Create a calendar event with Google Meet link and send email notifications."""
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
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{datetime.now().timestamp()}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        }
    }

    print(event_body)

    if participants:
        event_body["attendees"] = [{"email": e} for e in participants]

    try:
        calendar_service, gmail_service = get_services()

        created_event = (
            calendar_service.events()
            .insert(calendarId="primary", body=event_body, conferenceDataVersion=1, sendUpdates="all")
            .execute()
        )

        # Send email notifications to all participants
        meet_link = created_event.get("hangoutLink", "No Meet link")
        event_link = created_event.get('htmlLink', '')
        
        for email in participants:
            # Format datetime with timezone info for better readability
            timezone_name = start_dt.tzname() or "UTC"
            start_formatted = start_dt.strftime("%A, %B %d, %Y at %I:%M %p")
            if start_dt.tzinfo:
                start_formatted += f" ({timezone_name})"
            end_formatted = end_dt.strftime("%I:%M %p")
            
            html_body = f"""
                <h2 class="meeting-title">{title}</h2>
                
                <div class="info-card">
                    <div class="info-label">📝 AGENDA</div>
                    <div class="info-value">{agenda or 'No agenda provided'}</div>
                </div>
                
                <div class="info-card">
                    <div class="info-label">🕒 DATE & TIME</div>
                    <div class="info-value">{start_formatted}</div>
                    <div class="info-value" style="margin-top: 8px; font-size: 16px; color: #667eea;">⏱️ Duration: {duration_minutes} minutes</div>
                </div>
                
                <div class="divider"></div>
                
                <div class="button-container">
                    <a href="{meet_link}" class="button meet-button">📹 Join Google Meet</a>
                    <a href="{event_link}" class="button calendar-button">📅 View in Calendar</a>
                </div>
                
                <div class="tips-section">
                    <div class="tips-title">💡 Quick Tips</div>
                    <ul class="tips-list">
                        <li>Add this event to your calendar for reminders</li>
                        <li>Join the meeting 2-3 minutes early</li>
                        <li>Review the agenda and prepare materials</li>
                        <li>Test your audio and video before joining</li>
                    </ul>
                </div>
            """
            
            plain_text = f"""You have been invited to '{title}'
Agenda: {agenda or 'No agenda provided'}
Start: {start_formatted}
Duration: {duration_minutes} minutes
Google Meet: {meet_link}
Event Link: {event_link}"""
            
            _send_email(
                gmail_service,
                to_email=email,
                subject=f"✉️ Invitation: {title}",
                body_text=html_body
            )

        return created_event

    except HttpError as he:
        print(f"Google Calendar API HttpError: {he}")
        print(f"Error details: {he.error_details if hasattr(he, 'error_details') else 'No details'}")
        raise RuntimeError(f"Google Calendar API error: {he}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise RuntimeError(f"Error creating event: {e}")
