---
name: youtube_music_publisher
description: Automate YouTube music channel publishing including AI music generation, MoviePy video rendering, Gemini SEO metadata, OpenCV thumbnail extraction, and YouTube Data API v3 upload.
---

# YouTube Music Publisher Skill

This skill allows Antigravity AI agents to orchestrate an end-to-end publishing pipeline for YouTube music channels.

## When to Use This Skill
Use this skill whenever you need to:
- Generate ambient, lofi, synthwave, or relaxation AI music tracks.
- Render high-definition 1080p MP4 videos with visual background templates.
- Produce SEO-optimized YouTube titles, descriptions, tags, and hashtags using Gemini 3 Pro.
- Extract high-quality keyframes for YouTube video thumbnails using OpenCV.
- Upload videos and custom thumbnails to YouTube automatically via YouTube Data API v3.

## Workflows & Commands

### 1. Run Complete End-to-End Pipeline
Execute the full publishing workflow from music prompt to YouTube upload:
```bash
python cli.py run-all --prompt "<MUSIC_PROMPT>" --genre "<GENRE>" --mood "<MOOD>" --duration <SECONDS>
```

### 2. Generate SEO Metadata Only
Generate Pydantic-validated YouTube SEO metadata using Gemini:
```bash
python cli.py seo-only --prompt "<CONCEPT>" --genre "<GENRE>" --mood "<MOOD>"
```

### 3. Generate Audio Only
Generate audio track using APIMart Google Flow Music (or fallback):
```bash
python cli.py generate-music --prompt "<PROMPT>" --duration <SECONDS>
```

### 4. Direct Python Integration
```python
from youtube_music_automation.pipeline import PublishingPipeline

pipeline = PublishingPipeline(use_music_fallback=True)
result = pipeline.run(
    music_prompt="Late night rainy lofi chill beats",
    genre="Lofi",
    mood="Relaxing",
    audio_duration_seconds=30
)
print("Uploaded Video URL:", result['youtube']['url'])
```

## Environment Requirements
Ensure `.env` contains:
- `GEMINI_API_KEY`: API key for Gemini SEO generation.
- `APIMART_API_KEY`: API key for Google Flow Music audio generation.
- `YOUTUBE_CLIENT_SECRETS_FILE`: OAuth secrets for YouTube Data API v3.
