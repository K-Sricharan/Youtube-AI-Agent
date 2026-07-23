import os
import time
import math
import struct
import wave
import requests
from pathlib import Path
from typing import Optional

from youtube_music_automation.music.base import BaseMusicGenerator
from youtube_music_automation.config.settings import settings
from youtube_music_automation.utils.logger import get_logger
from youtube_music_automation.utils.retry import retry_on_exception

logger = get_logger("music_generator")

class APIMartFlowMusicGenerator(BaseMusicGenerator):
    """Integrates with APIMart / Google Flow Music API for programmatic audio generation."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.apimart_api_key
        self.base_url = base_url or settings.apimart_base_url

    @retry_on_exception(max_retries=3, delay=3.0)
    def generate_track(self, prompt: str, duration_seconds: int = 180, output_path: str = "output/generated_track.mp3") -> str:
        """Triggers audio generation via APIMart Flow Music API endpoints."""
        if not self.api_key or self.api_key == "your_apimart_api_key_here":
            logger.warning("APIMART_API_KEY not configured. Falling back to local synthetic audio generator.")
            fallback = FallbackMusicGenerator()
            return fallback.generate_track(prompt, duration_seconds, output_path)

        logger.info(f"Submitting Flow Music generation job for prompt: '{prompt}' (Duration: {duration_seconds}s)...")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "duration": duration_seconds,
            "model": "google-flow-music-v1"
        }

        try:
            response = requests.post(f"{self.base_url}/music/generate", json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data.get("task_id")

            logger.info(f"Generation job created with Task ID: {task_id}. Polling for completion...")
            # Poll status
            for _ in range(60):
                time.sleep(5)
                status_res = requests.get(f"{self.base_url}/music/tasks/{task_id}", headers=headers, timeout=15)
                if status_res.status_code == 200:
                    status_data = status_res.json()
                    status = status_data.get("status")
                    if status == "completed":
                        audio_url = status_data.get("audio_url")
                        logger.info(f"Audio generation completed. Downloading from {audio_url}...")
                        return self._download_file(audio_url, output_path)
                    elif status == "failed":
                        raise RuntimeError(f"Music generation task failed: {status_data.get('error')}")

            raise TimeoutError("Music generation timed out after 5 minutes.")

        except Exception as e:
            logger.error(f"APIMart API error: {e}. Switching to synthetic audio generator fallback.")
            fallback = FallbackMusicGenerator()
            return fallback.generate_track(prompt, duration_seconds, output_path)

    def _download_file(self, url: str, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Successfully saved generated track to {output_path}")
        return str(Path(output_path).resolve())


class FallbackMusicGenerator(BaseMusicGenerator):
    """Generates a pleasant ambient chord audio file locally using Python's standard wave library."""

    def generate_track(self, prompt: str, duration_seconds: int = 15, output_path: str = "output/sample_ambient_track.wav") -> str:
        logger.info(f"Generating synthetic fallback ambient track for prompt: '{prompt}' ({duration_seconds}s)...")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        sample_rate = 44100
        num_samples = sample_rate * duration_seconds
        num_channels = 2
        sample_width = 2

        # Pleasant ambient chord frequencies (C major 7 / A minor chords)
        freqs = [261.63, 329.63, 392.00, 493.88]

        wav_path = str(Path(output_path).with_suffix(".wav"))
        with wave.open(wav_path, "w") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Envelope for smooth fade-in and fade-out
                envelope = min(t / 2.0, 1.0) * min((duration_seconds - t) / 2.0, 1.0)
                
                # Combine chord frequencies with low LFO modulation
                lfo = 0.8 + 0.2 * math.sin(2 * math.pi * 0.2 * t)
                sample_val = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
                sample_val *= envelope * lfo * 0.5

                int_val = int(sample_val * 32767)
                int_val = max(-32768, min(32767, int_val))
                packed_sample = struct.pack("<h", int_val)
                frames.extend(packed_sample * num_channels)

            wav_file.writeframes(frames)

        logger.info(f"Synthetic ambient track generated at: {wav_path}")
        return str(Path(wav_path).resolve())
