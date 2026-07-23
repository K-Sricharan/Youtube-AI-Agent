import time
import random
from apscheduler.schedulers.blocking import BlockingScheduler
from youtube_music_automation.pipeline import PublishingPipeline
from youtube_music_automation.config.settings import settings
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("scheduler")

PROMPTS = [
    ("Midnight Lofi Beats for Deep Focus and Coding", "Lofi Chill", "Deep Focus"),
    ("Serene Ambient Soundscape for Sleep and Meditation", "Ambient", "Calm & Peaceful"),
    ("Upbeat Cyberpunk Synthwave for Gaming", "Synthwave", "Energetic"),
    ("Rainy Day Jazz Beats for Reading", "Jazz Lofi", "Relaxing"),
]

def scheduled_job():
    """Triggered job to run publishing pipeline periodically."""
    logger.info("Scheduler triggered! Selecting next track concept...")
    prompt, genre, mood = random.choice(PROMPTS)
    logger.info(f"Executing pipeline for: '{prompt}'")

    pipeline = PublishingPipeline(use_music_fallback=True)
    try:
        result = pipeline.run(
            music_prompt=prompt,
            genre=genre,
            mood=mood,
            audio_duration_seconds=30,
            privacy_status="unlisted"
        )
        logger.info(f"Scheduled pipeline finished successfully! Video URL: {result['youtube']['url']}")
    except Exception as e:
        logger.error(f"Scheduled job execution error: {e}")

def start_scheduler():
    """Starts the APScheduler blocking background loop."""
    interval_hours = settings.schedule_interval_hours
    logger.info(f"Starting YouTube Publishing Scheduler (Interval: Every {interval_hours} hours)...")

    scheduler = BlockingScheduler()
    # Schedule job every N hours
    scheduler.add_job(scheduled_job, 'interval', hours=interval_hours)

    try:
        scheduled_job()  # Initial run on startup
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")

if __name__ == "__main__":
    start_scheduler()
