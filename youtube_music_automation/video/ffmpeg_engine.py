import os
import subprocess
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

from youtube_music_automation.utils.logger import get_logger
from youtube_music_automation.utils.retry import retry_on_exception

logger = get_logger("video_engine")

class VideoCreatorEngine:
    """Renders high-definition MP4 videos by overlaying audio onto static/looping background templates."""

    def __init__(self, default_template: Optional[str] = None):
        self.default_template = default_template or "templates/sample_background.png"

    def ensure_default_template(self) -> str:
        """Generates a stylish, modern 1080p ambient gradient background image if none exists."""
        template_path = Path(self.default_template)
        template_path.parent.mkdir(parents=True, exist_ok=True)

        if not template_path.exists():
            logger.info(f"Creating modern default 1080p background template at '{template_path}'...")
            img = Image.new("RGB", (1920, 1080), color=(18, 18, 28))
            draw = ImageDraw.Draw(img)

            # Draw sleek radial glow lines / gradient aesthetic
            for r in range(500, 0, -10):
                alpha_val = int(255 * (1 - r / 500))
                color = (30 + int(r * 0.1), 25 + int(r * 0.05), 60 + int(r * 0.2))
                draw.ellipse([960 - r, 540 - r, 960 + r, 540 + r], fill=color)

            # Draw subtle center branding text
            draw.text((960, 540), "AUDIO SOUNDSCAPE", fill=(220, 220, 255), anchor="mm")
            img.save(template_path)
            logger.info(f"Default background template saved: {template_path}")

        return str(template_path.resolve())

    @retry_on_exception(max_retries=2, delay=2.0)
    def create_video(
        self,
        audio_path: str,
        template_path: Optional[str] = None,
        output_path: str = "output/final_video.mp4",
        fps: int = 24
    ) -> str:
        """Combines audio file with background template image/video using MoviePy or direct FFmpeg execution."""
        bg_path = template_path or self.ensure_default_template()
        if not Path(bg_path).exists():
            bg_path = self.ensure_default_template()

        logger.info(f"Rendering video with Audio='{audio_path}', Template='{bg_path}' -> Output='{output_path}'...")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Attempt rendering via MoviePy (supporting both MoviePy v1 and v2)
        try:
            try:
                from moviepy import AudioFileClip, ImageClip, VideoFileClip
            except ImportError:
                from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip

            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration

            if bg_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                video_clip = ImageClip(bg_path).with_duration(duration) if hasattr(ImageClip(bg_path), 'with_duration') else ImageClip(bg_path).set_duration(duration)
            else:
                video_clip = VideoFileClip(bg_path)
                if hasattr(video_clip, 'with_duration'):
                    video_clip = video_clip.with_duration(duration)
                else:
                    video_clip = video_clip.set_duration(duration)

            final_clip = video_clip.with_audio(audio_clip) if hasattr(video_clip, 'with_audio') else video_clip.set_audio(audio_clip)
            
            temp_audio = str(Path(output_path).with_suffix(".temp.m4a"))
            final_clip.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=temp_audio,
                remove_temp=True,
                logger=None
            )
            audio_clip.close()
            final_clip.close()

            logger.info(f"Video rendered successfully using MoviePy: {output_path}")
            return str(Path(output_path).resolve())

        except Exception as e:
            logger.warning(f"MoviePy rendering failed ({e}). Attempting direct FFmpeg executable fallback...")
            return self._ffmpeg_cli_fallback(audio_path, bg_path, output_path)

    def _ffmpeg_cli_fallback(self, audio_path: str, bg_path: str, output_path: str) -> str:
        """Fallback video renderer using imageio_ffmpeg binary or system ffmpeg."""
        ffmpeg_bin = "ffmpeg"
        try:
            import imageio_ffmpeg
            ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

        cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1",
            "-i", bg_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        logger.info(f"Executing FFmpeg CLI command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg CLI rendering failed: {result.stderr}")

        logger.info(f"FFmpeg CLI rendering succeeded: {output_path}")
        return str(Path(output_path).resolve())
