import click
import json
from youtube_music_automation.pipeline import PublishingPipeline
from youtube_music_automation.seo.gemini_agent import GeminiSEOAgent
from youtube_music_automation.music.manager import MusicManager
from youtube_music_automation.video.ffmpeg_engine import VideoCreatorEngine
from youtube_music_automation.thumbnail.extractor import ThumbnailExtractor

@click.group()
def cli():
    """YouTube Music Automation CLI Tool."""
    pass

@cli.command()
@click.option('--prompt', required=True, help='Music generation text prompt.')
@click.option('--genre', default='Lofi Chill', help='Music genre.')
@click.option('--mood', default='Relaxing', help='Music mood.')
@click.option('--duration', default=20, help='Audio track duration in seconds.')
@click.option('--privacy', default='unlisted', help='YouTube privacy status (public, unlisted, private).')
@click.option('--fallback-music', is_flag=True, help='Force fallback synthetic audio generator.')
def run_all(prompt, genre, mood, duration, privacy, fallback_music):
    """Run full end-to-end publishing pipeline."""
    click.echo(f"Starting full pipeline for prompt: '{prompt}'...")
    pipeline = PublishingPipeline(use_music_fallback=fallback_music)
    result = pipeline.run(
        music_prompt=prompt,
        genre=genre,
        mood=mood,
        audio_duration_seconds=duration,
        privacy_status=privacy
    )
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.option('--prompt', required=True, help='Prompt for Gemini SEO generation.')
@click.option('--genre', default='Ambient', help='Genre.')
@click.option('--mood', default='Focus', help='Mood.')
def seo_only(prompt, genre, mood):
    """Generate SEO metadata only."""
    agent = GeminiSEOAgent()
    metadata = agent.generate_seo_metadata(prompt, genre, mood)
    click.echo(json.dumps(metadata.model_dump(), indent=2))

@cli.command()
@click.option('--video', required=True, type=str, help='Path to your local video file (.mp4, .mov, etc.).')
@click.option('--title', required=True, help='Title for your YouTube video.')
@click.option('--genre', default='Music', help='Genre or topic category.')
@click.option('--mood', default='Relaxing', help='Mood or vibe.')
@click.option('--privacy', default='public', help='YouTube privacy status (public, unlisted, private).')
def upload_video(video, title, genre, mood, privacy):
    """Upload your own video: generates Gemini description & tags, extracts thumbnail, and uploads to YouTube."""
    click.echo(f"Processing user video: '{video}' with Title: '{title}'...")
    pipeline = PublishingPipeline()
    result = pipeline.publish_user_video(
        video_path=video,
        title=title,
        genre=genre,
        mood=mood,
        privacy_status=privacy
    )
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.option('--folder', required=True, type=str, help='Path to directory containing video/audio files.')
@click.option('--genre', default='Music', help='Genre or category.')
@click.option('--mood', default='Relaxing', help='Mood or vibe.')
@click.option('--privacy', default='public', help='YouTube privacy status (public, unlisted, private).')
def upload_folder(folder, genre, mood, privacy):
    """Batch upload all video/audio files from a directory to YouTube."""
    from pathlib import Path
    f_path = Path(folder).resolve()
    if not f_path.exists() or not f_path.is_dir():
        click.echo(f"Error: Folder '{folder}' does not exist or is not a directory.")
        return

    valid_exts = ('.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.flac', '.m4a')
    files = [str(p) for p in f_path.iterdir() if p.suffix.lower() in valid_exts]

    if not files:
        click.echo(f"No video/audio files found in folder '{folder}'.")
        return

    click.echo(f"Found {len(files)} files in '{folder}'. Starting batch publishing pipeline...")
    pipeline = PublishingPipeline()
    results = pipeline.batch_publish_user_videos(
        files=files,
        genre=genre,
        mood=mood,
        privacy_status=privacy
    )
    click.echo(json.dumps(results, indent=2))

if __name__ == '__main__':
    cli()

