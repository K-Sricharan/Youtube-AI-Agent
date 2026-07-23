import os
from pathlib import Path
from typing import Optional, Any
from youtube_music_automation.config.settings import settings
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("youtube_auth")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_authenticated_youtube_service(
    client_secrets_file: Optional[str] = None,
    token_file: Optional[str] = None
) -> Any:
    """Authenticates and returns a YouTube Data API v3 service instance."""
    secrets_path = client_secrets_file or settings.youtube_client_secrets_file
    token_path = token_file or settings.youtube_token_file

    if not Path(secrets_path).exists() and not Path(token_path).exists():
        logger.warning(
            f"YouTube OAuth client secrets file '{secrets_path}' or token file '{token_path}' not found. "
            "YouTube uploader will run in simulated mode until Google Cloud OAuth credentials are provided."
        )
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        if Path(token_path).exists():
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired YouTube OAuth credentials...")
                try:
                    creds.refresh(Request())
                except Exception as refresh_err:
                    logger.warning(f"Failed to refresh OAuth token ({refresh_err}). Removing stale token and re-authenticating...")
                    if Path(token_path).exists():
                        os.remove(token_path)
                    creds = None

            if not creds:
                if not Path(secrets_path).exists():
                    raise FileNotFoundError(f"Cannot initialize new OAuth flow without '{secrets_path}'")
                logger.info("Initiating local YouTube OAuth authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())
                logger.info(f"Saved OAuth tokens to '{token_path}'")

        return build("youtube", "v3", credentials=creds)

    except Exception as e:
        logger.error(f"Error authenticating with YouTube Data API: {e}")
        return None
