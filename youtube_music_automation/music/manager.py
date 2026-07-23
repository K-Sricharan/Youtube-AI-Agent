import os
from pathlib import Path
from youtube_music_automation.music.flow_music import APIMartFlowMusicGenerator, FallbackMusicGenerator
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("music_manager")

class MusicManager:
    """Manages audio generation, provider selection, and audio validation."""

    def __init__(self, use_fallback: bool = False):
        if use_fallback:
            self.provider = FallbackMusicGenerator()
        else:
            self.provider = APIMartFlowMusicGenerator()

    def generate_and_verify(self, prompt: str, duration_seconds: int = 30, output_path: str = "output/track.wav") -> str:
        """Generates audio track and verifies file existence and non-zero size."""
        track_path = self.provider.generate_track(prompt, duration_seconds, output_path)
        
        path_obj = Path(track_path)
        if not path_obj.exists() or path_obj.stat().st_size == 0:
            raise FileNotFoundError(f"Generated track at '{track_path}' is invalid or empty.")
            
        logger.info(f"Verified generated audio track: {track_path} (Size: {path_obj.stat().st_size} bytes)")
        return track_path
