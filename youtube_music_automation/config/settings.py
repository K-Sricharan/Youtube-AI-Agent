import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Gemini Settings
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model_name: str = Field(default="gemini-2.5-pro", env="GEMINI_MODEL_NAME")

    # APIMart / Flow Music Settings
    apimart_api_key: str = Field(default="", env="APIMART_API_KEY")
    apimart_base_url: str = Field(default="https://api.apimart.ai/v1", env="APIMART_BASE_URL")

    # YouTube API Settings
    youtube_client_secrets_file: str = Field(default="client_secrets.json", env="YOUTUBE_CLIENT_SECRETS_FILE")
    youtube_token_file: str = Field(default="token.json", env="YOUTUBE_TOKEN_FILE")
    youtube_privacy_status: str = Field(default="unlisted", env="YOUTUBE_PRIVACY_STATUS")

    # Directory Paths
    templates_dir: str = Field(default="templates", env="TEMPLATES_DIR")
    output_dir: str = Field(default="output", env="OUTPUT_DIR")
    logs_dir: str = Field(default="logs", env="LOGS_DIR")
    default_background_template: str = Field(default="templates/sample_background.png", env="DEFAULT_BACKGROUND_TEMPLATE")

    # Schedule Settings
    schedule_interval_hours: int = Field(default=24, env="SCHEDULE_INTERVAL_HOURS")

    def ensure_directories(self) -> None:
        """Create output, templates, and logs directories if they don't exist."""
        for path_str in [self.templates_dir, self.output_dir, self.logs_dir]:
            Path(path_str).mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
