import sys
from youtube_music_automation.pipeline import PublishingPipeline
from youtube_music_automation.utils.logger import get_logger

logger = get_logger("main")

def main():
    """Main entry point to test and execute the publishing pipeline."""
    prompt = "Cosmic lofi beats for late night coding and relaxation"
    genre = "Lofi Chill"
    mood = "Calm & Reflective"

    logger.info(f"Running main workflow pipeline with sample prompt: '{prompt}'...")
    pipeline = PublishingPipeline(use_music_fallback=True)
    result = pipeline.run(
        music_prompt=prompt,
        genre=genre,
        mood=mood,
        audio_duration_seconds=15,
        privacy_status="unlisted"
    )

    print("\n" + "="*50)
    print(" PIPELINE EXECUTION SUMMARY")
    print("="*50)
    print(f" Status:        {result['status']}")
    print(f" Video Path:    {result['video_path']}")
    print(f" Thumbnail:     {result['thumbnail_path']}")
    print(f" Video Title:   {result['seo_metadata']['title']}")
    print(f" YouTube URL:   {result['youtube']['url']} (Simulated: {result['youtube']['is_simulated']})")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
