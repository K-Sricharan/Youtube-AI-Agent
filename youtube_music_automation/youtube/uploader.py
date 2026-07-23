import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

from youtube_music_automation.config.settings import settings
from youtube_music_automation.seo.schemas import YouTubeSEOOutput
from youtube_music_automation.youtube.auth import get_authenticated_youtube_service
from youtube_music_automation.utils.logger import get_logger
from youtube_music_automation.utils.retry import retry_on_exception

logger = get_logger("youtube_uploader")

class YouTubeUploader:
    """Uploads videos and custom thumbnails to YouTube using official Data API v3."""

    def __init__(self, service: Any = None):
        self.service = service or get_authenticated_youtube_service()

    @retry_on_exception(max_retries=3, delay=5.0)
    def upload_video_and_thumbnail(
        self,
        video_path: str,
        metadata: YouTubeSEOOutput,
        thumbnail_path: Optional[str] = None,
        privacy_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uploads video with metadata and attaches custom thumbnail."""
        privacy = privacy_status or settings.youtube_privacy_status
        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        if not self.service:
            logger.warning(
                "YouTube API service is not authenticated. Executing simulated dry-run upload..."
            )
            return self._simulated_upload(video_path, metadata, thumbnail_path, privacy)

        from googleapiclient.http import MediaFileUpload

        # Sanitize and truncate tags to meet YouTube API specs (< 450 total chars, clean strings)
        sanitized_tags = []
        total_len = 0
        if metadata.tags:
            for tag in metadata.tags:
                clean_tag = str(tag).replace("<", "").replace(">", "").replace("\n", "").replace(",", "").strip()
                if clean_tag and len(clean_tag) <= 50:
                    if total_len + len(clean_tag) + 1 <= 450:
                        sanitized_tags.append(clean_tag)
                        total_len += len(clean_tag) + 1

        body = {
            "snippet": {
                "title": metadata.title[:95] if len(metadata.title) > 95 else metadata.title,
                "description": metadata.description[:4900] if len(metadata.description) > 4900 else metadata.description,
                "tags": sanitized_tags,
                "categoryId": metadata.category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            }
        }

        logger.info(f"Initiating resumable upload for '{video_path}' (Privacy: {privacy})...")
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            chunksize=1024 * 1024 * 5,  # 5MB chunks
            resumable=True
        )

        insert_request = self.service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"YouTube Upload Progress: {progress}%")

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        logger.info(f"Video successfully uploaded! ID: {video_id} | URL: {video_url}")

        # Upload custom thumbnail if available
        if thumbnail_path and Path(thumbnail_path).exists():
            self._upload_thumbnail(video_id, thumbnail_path)

        return {
            "video_id": video_id,
            "url": video_url,
            "title": metadata.title,
            "status": privacy,
            "is_simulated": False
        }

    def _upload_thumbnail(self, video_id: str, thumbnail_path: str) -> None:
        """Uploads custom thumbnail image for an existing YouTube video ID."""
        try:
            from googleapiclient.http import MediaFileUpload
            logger.info(f"Uploading thumbnail '{thumbnail_path}' for video ID '{video_id}'...")
            media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logger.info("Custom thumbnail attached successfully!")
        except Exception as e:
            logger.error(f"Failed to upload thumbnail: {e}")

    def _simulated_upload(
        self,
        video_path: str,
        metadata: YouTubeSEOOutput,
        thumbnail_path: Optional[str],
        privacy: str
    ) -> Dict[str, Any]:
        """Provides simulated return object when YouTube API credentials are absent."""
        simulated_id = f"sim_{int(time.time())}"
        simulated_url = f"https://youtu.be/{simulated_id}"
        logger.info(f"[SIMULATED UPLOAD] Title: '{metadata.title}'")
        logger.info(f"[SIMULATED UPLOAD] URL: {simulated_url} (Privacy: {privacy})")
        if thumbnail_path:
            logger.info(f"[SIMULATED UPLOAD] Custom Thumbnail: {thumbnail_path}")

        return {
            "video_id": simulated_id,
            "url": simulated_url,
            "title": metadata.title,
            "status": privacy,
            "is_simulated": True
        }
