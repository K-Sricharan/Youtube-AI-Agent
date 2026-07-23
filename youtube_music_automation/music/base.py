from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseMusicGenerator(ABC):
    """Abstract base class for all AI music generation backends."""

    @abstractmethod
    def generate_track(self, prompt: str, duration_seconds: int = 180, output_path: str = "output/track.mp3") -> str:
        """Generates audio for a given prompt and returns the absolute path to the saved file."""
        pass
