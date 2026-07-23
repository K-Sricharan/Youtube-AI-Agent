import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from youtube_music_automation.config.settings import settings
from youtube_music_automation.music.manager import MusicManager
from youtube_music_automation.video.ffmpeg_engine import VideoCreatorEngine
from youtube_music_automation.seo.gemini_agent import GeminiSEOAgent
from youtube_music_automation.seo.schemas import YouTubeSEOOutput
from youtube_music_automation.thumbnail.extractor import ThumbnailExtractor
from youtube_music_automation.youtube.uploader import YouTubeUploader
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("publishing_pipeline")

class PublishingPipeline:
    """End-to-end publishing pipeline for automated AI YouTube music channels."""

    def __init__(
        self,
        use_music_fallback: bool = False,
        background_template: Optional[str] = None
    ):
        self.music_manager = MusicManager(use_fallback=use_music_fallback)
        self.video_engine = VideoCreatorEngine(default_template=background_template)
        self.seo_agent = GeminiSEOAgent()
        self.thumbnail_extractor = ThumbnailExtractor()
        self.youtube_uploader = YouTubeUploader()

    def run(
        self,
        music_prompt: str,
        genre: str = "Lo-Fi Beats",
        mood: str = "Relaxing & Chill",
        audio_duration_seconds: int = 20,
        background_template: Optional[str] = None,
        privacy_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes the complete publishing workflow end-to-end."""
        logger.info("=" * 60)
        logger.info("STARTING YOUTUBE MUSIC PUBLISHING PIPELINE WORKFLOW")
        logger.info(f"Prompt: '{music_prompt}' | Genre: '{genre}' | Mood: '{mood}'")
        logger.info("=" * 60)

        # Step 1: Generate AI Music Track
        logger.info("---> Step 1/5: Music Generation...")
        audio_output = str(Path(settings.output_dir) / "generated_track.wav")
        audio_path = self.music_manager.generate_and_verify(
            prompt=music_prompt,
            duration_seconds=audio_duration_seconds,
            output_path=audio_output
        )

        # Step 2: Render Video
        logger.info("---> Step 2/5: Video Creation...")
        video_output = str(Path(settings.output_dir) / "output_video.mp4")
        video_path = self.video_engine.create_video(
            audio_path=audio_path,
            template_path=background_template,
            output_path=video_output
        )

        # Step 3: Generate SEO Metadata via Gemini Agent
        logger.info("---> Step 3/5: Gemini SEO Metadata Generation...")
        seo_metadata: YouTubeSEOOutput = self.seo_agent.generate_seo_metadata(
            music_prompt=music_prompt,
            genre=genre,
            mood=mood
        )

        # Step 4: Extract & Enhance Thumbnail (Middle Frame)
        logger.info("---> Step 4/5: Thumbnail Extraction (Middle Frame)...")
        thumb_output = str(Path(settings.output_dir) / "thumbnail.jpg")
        thumbnail_path = self.thumbnail_extractor.extract_thumbnail(
            video_path=video_path,
            output_path=thumb_output,
            timestamp_sec=None,
            title_overlay=None
        )

        # Step 5: Publish to YouTube
        logger.info("---> Step 5/5: YouTube Publishing...")
        upload_result = self.youtube_uploader.upload_video_and_thumbnail(
            video_path=video_path,
            metadata=seo_metadata,
            thumbnail_path=thumbnail_path,
            privacy_status=privacy_status
        )

        logger.info("=" * 60)
        logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        logger.info(f"Video URL: {upload_result.get('url')}")
        logger.info(f"Title: {seo_metadata.title}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "audio_path": audio_path,
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "seo_metadata": seo_metadata.model_dump(),
            "youtube": upload_result
        }

    def publish_user_video(
        self,
        video_path: str,
        title: str,
        genre: str = "Music",
        mood: str = "Relaxing",
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """Processes an existing user video: generates Gemini SEO description & tags, extracts thumbnail, and uploads to YouTube."""
        logger.info("=" * 60)
        logger.info("PROCESSING USER VIDEO FOR YOUTUBE PUBLISHING")
        logger.info(f"Video File: '{video_path}' | Title: '{title}'")
        logger.info("=" * 60)

        v_path = Path(video_path).resolve()
        if not v_path.exists():
            raise FileNotFoundError(f"Video or audio file not found: '{video_path}'. Please make sure the file path is correct.")
        video_path = str(v_path)

        # If user passed an audio file (.mp3, .wav, etc.), automatically render it into a 1080p MP4 video
        if v_path.suffix.lower() in ('.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg'):
            logger.info(f"Input file '{v_path.name}' is an audio track. Automatically rendering 1080p MP4 video...")
            video_output = str(Path(settings.output_dir) / f"{v_path.stem}_rendered.mp4")
            video_path = self.video_engine.create_video(
                audio_path=video_path,
                output_path=video_output
            )
            logger.info(f"Audio rendered into video: {video_path}")

        # Step 1: Generate SEO Metadata (Description, Tags, Hashtags) via Gemini
        logger.info("---> Step 1/3: Generating Description & SEO Tags via Gemini...")
        seo_metadata: YouTubeSEOOutput = self.seo_agent.generate_seo_metadata(
            music_prompt=title,
            genre=genre,
            mood=mood
        )
        # Override title with user specified title
        seo_metadata.title = title

        # Step 2: Extract High Quality Middle Frame for Thumbnail
        logger.info("---> Step 2/3: Extracting Keyframe Thumbnail (Middle Frame)...")
        thumb_output = str(Path(settings.output_dir) / f"thumb_{Path(video_path).stem}.jpg")
        thumbnail_path = self.thumbnail_extractor.extract_thumbnail(
            video_path=video_path,
            output_path=thumb_output,
            timestamp_sec=None,
            title_overlay=None
        )

        # Step 3: Upload Video and Thumbnail to YouTube Channel
        logger.info("---> Step 3/3: Uploading Video and Thumbnail to YouTube...")
        upload_result = self.youtube_uploader.upload_video_and_thumbnail(
            video_path=video_path,
            metadata=seo_metadata,
            thumbnail_path=thumbnail_path,
            privacy_status=privacy_status
        )

        logger.info("=" * 60)
        logger.info("USER VIDEO PUBLISHED SUCCESSFULLY!")
        logger.info(f"Video URL: {upload_result.get('url')}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "video_path": video_path,
            "thumbnail_path": thumbnail_path,
            "seo_metadata": seo_metadata.model_dump(),
            "youtube": upload_result
        }

    def batch_publish_user_videos(
        self,
        files: List[str],
        genre: str = "Music",
        mood: str = "Relaxing",
        privacy_status: str = "public"
    ) -> List[Dict[str, Any]]:
        """Processes and uploads multiple video/audio files sequentially."""
        logger.info(f"Starting batch upload for {len(files)} files...")
        results = []
        import time

        for idx, file_path in enumerate(files, 1):
            p = Path(file_path)
            clean_title = p.stem.replace("_", " ").replace("-", " ").title()
            logger.info(f"\n--- Batch Item [{idx}/{len(files)}]: '{p.name}' (Title: '{clean_title}') ---")

            try:
                res = self.publish_user_video(
                    video_path=file_path,
                    title=clean_title,
                    genre=genre,
                    mood=mood,
                    privacy_status=privacy_status
                )
                results.append(res)
            except Exception as e:
                logger.error(f"Failed batch item [{idx}/{len(files)}] '{file_path}': {e}")
                results.append({
                    "status": "error",
                    "video_path": file_path,
                    "error": str(e)
                })

            if idx < len(files):
                time.sleep(3)  # Brief pause between batch items

        return results

