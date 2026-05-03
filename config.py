from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # GROQ API settings
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Google Calendar settings
    google_credentials_file: str = "credentials.json"
    google_calendar_id: str = "primary"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()