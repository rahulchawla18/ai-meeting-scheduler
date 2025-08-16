from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # Google Calendar settings
    google_credentials_file: str = "credentials.json"  # Path to service account file
    google_calendar_id: str = "primary"  # Default calendar ID

def get_settings():
    return Settings()