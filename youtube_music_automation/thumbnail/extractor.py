import os
from pathlib import Path
from typing import Optional
try:
    import cv2
except ImportError:
    cv2 = None

from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("thumbnail_extractor")

class ThumbnailExtractor:
    """Extracts and enhances keyframes from video files for YouTube thumbnail upload using OpenCV and Pillow."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_thumbnail(
        self,
        video_path: str,
        output_path: str = "output/thumbnail.jpg",
        timestamp_sec: Optional[float] = None,
        title_overlay: Optional[str] = None
    ) -> str:
        """Extracts frame from video file at middle timestamp (or requested timestamp), enhances quality, and saves as JPEG."""
        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        if cv2 is None:
            logger.warning("OpenCV (cv2) is not installed. Utilizing high-quality Pillow image thumbnail generator fallback.")
            return self._create_fallback_thumbnail(output_path, title_overlay)

        # Open video with OpenCV
        cap = cv2.VideoCapture(str(video_file))
        if not cap.isOpened():
            logger.warning(f"Could not open video file via OpenCV: {video_path}. Using image template fallback.")
            return self._create_fallback_thumbnail(output_path, title_overlay)

        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration_sec = (total_frames / fps) if (total_frames > 0 and fps > 0) else 10.0

        # Default to middle frame if timestamp_sec is None or <= 0
        if timestamp_sec is None or timestamp_sec <= 0:
            timestamp_sec = max(1.0, duration_sec / 2.0)

        logger.info(f"Extracting thumbnail frame from '{video_path}' at middle t={timestamp_sec:.2f}s (duration: {duration_sec:.2f}s)...")

        # Move to target frame
        frame_id = int(fps * timestamp_sec)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            logger.warning(f"Failed to read frame at {timestamp_sec:.2f}s. Reading first available frame...")
            cap = cv2.VideoCapture(str(video_file))
            ret, frame = cap.read()
            cap.release()
            if not ret or frame is None:
                return self._create_fallback_thumbnail(output_path, title_overlay)

        # Convert BGR (OpenCV) to RGB (Pillow)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        # Enhance Image Quality (Contrast, Color, Sharpness)
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.10)
        img = ImageEnhance.Sharpness(img).enhance(1.20)

        # Add Title Overlay if provided
        if title_overlay:
            img = self._apply_title_overlay(img, title_overlay)

        # Save as high-quality JPEG (under 2MB for YouTube specs)
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        img.save(output_path, "JPEG", quality=92)

        logger.info(f"Successfully generated thumbnail at '{output_path}'")
        return str(Path(output_path).resolve())

    def _apply_title_overlay(self, img: Image.Image, text: str) -> Image.Image:
        """Overlays custom title text onto the thumbnail image."""
        draw = ImageDraw.Draw(img)
        w, h = img.size
        # Simple text banner
        text_banner = text.upper()
        if len(text_banner) > 35:
            text_banner = text_banner[:35] + "..."

        draw.rectangle([50, h - 150, w - 50, h - 50], fill=(0, 0, 0, 180))
        draw.text((w // 2, h - 100), text_banner, fill=(255, 255, 255), anchor="mm")
        return img

    def _create_fallback_thumbnail(self, output_path: str, title_overlay: Optional[str] = None) -> str:
        """Creates a modern 720p fallback thumbnail if video frame extraction fails."""
        img = Image.new("RGB", (1280, 720), color=(25, 25, 40))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 1240, 680], outline=(100, 100, 200), width=4)
        draw.text((640, 360), title_overlay or "OFFICIAL AUDIO TRACK", fill=(240, 240, 255), anchor="mm")
        img.save(output_path, "JPEG", quality=90)
        logger.info(f"Fallback thumbnail generated at '{output_path}'")
        return str(Path(output_path).resolve())
