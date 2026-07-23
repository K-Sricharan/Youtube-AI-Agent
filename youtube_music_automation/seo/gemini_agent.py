import os
import json
from typing import Optional, List
from youtube_music_automation.config.settings import settings
from youtube_music_automation.seo.schemas import YouTubeSEOOutput
from youtube_music_automation.utils.logger import get_logger
from youtube_music_automation.utils.retry import retry_on_exception

logger = get_logger("gemini_seo_agent")

class GeminiSEOAgent:
    """Agentic SEO tool using Gemini to produce YouTube metadata following user reference template."""

    SYSTEM_PROMPT = """
You are an elite YouTube Music SEO Specialist. Your task is to generate complete, high-ranking, production-grade metadata based strictly on the user's provided track title and details.

Format the description section exactly according to this reference structure:

Alternative Titles
[3-5 title variations with high-ranking keywords]

Description
[2-3 engaging sentences describing the audio track, instruments, rhythm, and atmosphere]

Music Information
Title: [Title]
Genre: [Genre]
Mood: [Mood]
BPM: [BPM]

Instruments
[List of featured instruments]

Perfect For
YouTube Videos
Gaming Videos
Travel Vlogs
Drone Footage
AI Generated Videos
Cinematic Videos
Motivational Videos
Short Films
Documentaries
Instagram Reels
TikTok Videos
Podcasts
Coding Sessions
Study Videos

License
You are free to use this music in your YouTube videos and social media content.
Please provide credit in your video description.

Credit Example
Music: [Title]
Artist: Your Channel Name
Link: Video URL

If you enjoy this music, please Like, Share, and Subscribe for more high-quality No Copyright Music.
Turn on notifications to stay updated with future uploads.

Chapters
00:00 Intro
00:28 Build Up
01:04 Drop
01:52 Breakdown
02:32 Final Drop
03:18 Outro

Hashtags
[10-15 trending hashtags starting with #]

SEO Keywords
[Comprehensive block of 40-50 relevant comma-separated SEO keywords including genre, mood, track title, use cases, and no copyright music search terms]
"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model_name

    @retry_on_exception(max_retries=3, delay=2.0)
    def generate_seo_metadata(
        self,
        music_prompt: str,
        genre: str = "Liquid Drum & Bass",
        mood: str = "Emotional • Atmospheric • Inspiring",
        bpm: int = 174
    ) -> YouTubeSEOOutput:
        """Generates YouTubeSEOOutput structured metadata matching user reference template."""
        logger.info(f"Generating reference-formatted SEO metadata for title: '{music_prompt}'")

        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.info("Utilizing deterministic rule-based template engine for YouTube SEO metadata.")
            return self._generate_fallback(music_prompt, genre, mood, bpm)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = (
                f"{self.SYSTEM_PROMPT}\n\n"
                f"Music Details:\n"
                f"- Provided Title: {music_prompt}\n"
                f"- Genre: {genre}\n"
                f"- Mood: {mood}\n"
                f"- BPM: {bpm}\n\n"
                f"Return JSON conforming to YouTubeSEOOutput."
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=YouTubeSEOOutput,
                    temperature=0.7,
                ),
            )

            if response.text:
                data = json.loads(response.text)
                return YouTubeSEOOutput(**data)

        except Exception as e:
            logger.error(f"Gemini API call failed ({e}). Falling back to rule-based template engine.")

        return self._generate_fallback(music_prompt, genre, mood, bpm)

    def _generate_fallback(self, title: str, genre: str, mood: str, bpm: int) -> YouTubeSEOOutput:
        """Generates exact reference-structured metadata offline or without Gemini key."""
        clean_title = title.strip()
        
        alt_titles = [
            f"{clean_title} | Emotional {genre} | Copyright Free Music",
            f"{clean_title} | {genre} | Royalty Free Background Music",
            f"{genre} No Copyright Music | {clean_title}",
            f"{clean_title} | Atmospheric Music | Free Music for Creators",
            f"{clean_title} | Emotional Gaming Music | Copyright Free"
        ]

        instruments = [
            "Soulful Electric Piano",
            "Atmospheric Pads",
            "Deep Sub Bass",
            "Breakbeats",
            "Ambient Synths",
            "Ethereal Vocal Chops"
        ]

        perfect_for = [
            "YouTube Videos",
            "Gaming Videos",
            "Travel Vlogs",
            "Drone Footage",
            "AI Generated Videos",
            "Cinematic Videos",
            "Motivational Videos",
            "Short Films",
            "Documentaries",
            "Instagram Reels",
            "TikTok Videos",
            "Facebook Videos",
            "Podcasts",
            "Coding Sessions",
            "Study Videos",
            "Product Advertisements"
        ]

        hashtags = [
            "#NoCopyrightMusic",
            "#CopyrightFreeMusic",
            f"#{genre.replace(' ', '').replace('&', 'And').replace('/', '')}",
            "#BackgroundMusic",
            "#GamingMusic",
            "#RoyaltyFreeMusic",
            "#ElectronicMusic",
            "#AtmosphericMusic",
            "#EmotionalMusic",
            "#FreeMusic",
            "#YouTubeMusic",
            "#CreatorMusic",
            "#VlogMusic"
        ]

        description_text = (
            f"Experience {clean_title}, an emotional {genre} journey featuring soulful piano melodies, "
            f"atmospheric synths, deep sub bass, crisp breakbeats, and ethereal vocal chops.\n\n"
            f"Designed for creators who need high-quality copyright free music, this track is perfect for "
            f"YouTube videos, gaming montages, cinematic films, AI-generated videos, travel vlogs, documentaries, "
            f"motivational edits, and more.\n\n"
            f"--- Alternative Titles ---\n" + "\n".join(alt_titles) + "\n\n"
            f"--- Music Information ---\n"
            f"Title: {clean_title}\n"
            f"Genre: {genre}\n"
            f"Mood: {mood}\n"
            f"BPM: {bpm}\n\n"
            f"--- Instruments ---\n" + "\n".join(f"• {inst}" for inst in instruments) + "\n\n"
            f"--- Perfect For ---\n" + "\n".join(f"• {pf}" for pf in perfect_for) + "\n\n"
            f"--- License ---\n"
            f"You are free to use this music in your YouTube videos and social media content.\n"
            f"Please provide credit in your video description.\n\n"
            f"Credit Example:\n"
            f"Music: {clean_title}\n"
            f"Artist: Your Channel Name\n"
            f"Link: Video URL\n\n"
            f"If you enjoy this music, please Like, Share, and Subscribe for more high-quality No Copyright Music.\n"
            f"Turn on notifications to stay updated with future uploads.\n\n"
            f"--- Chapters ---\n"
            f"00:00 Intro\n"
            f"00:28 Build Up\n"
            f"01:04 Drop\n"
            f"01:52 Breakdown\n"
            f"02:32 Final Drop\n"
            f"03:18 Outro\n\n"
            f"--- Hashtags ---\n" + " ".join(hashtags) + "\n\n"
            f"--- SEO Keywords ---\n"
            f"{genre}, No Copyright Music, Copyright Free Music, Royalty Free Music, Free Background Music, "
            f"Electronic Music, Atmospheric Music, Emotional Music, Deep Bass, Soulful Piano, Breakbeats, "
            f"Gaming Music, Travel Vlog Music, Drone Footage Music, Documentary Music, AI Video Music, "
            f"AI Generated Video Music, Cinematic Music, Storytelling Music, Motivational Music, Inspiring Music, "
            f"Relaxing Electronic Music, Study Music, Coding Music, Editing Music, YouTube Music, Music For Creators, "
            f"Creator Background Music, Copyright Safe Music, Stream Safe Music, Twitch Music, Instagram Reels Music, "
            f"TikTok Music, Shorts Music, YouTube Shorts Music, Cinematic Electronic Music, Ambient Electronic, "
            f"Background Music For Videos, Royalty Free Soundtrack, Modern Electronic Music, Professional Background Music, "
            f"Best No Copyright Music, Trending No Copyright Music, Viral Background Music, High Quality Music, "
            f"Free Instrumental Music, YouTube Monetization Safe Music, Royalty Free Audio, Background Soundtrack, "
            f"Vlog Music, Adventure Music, Nature Music, Ocean Music, {clean_title}, {clean_title} Music."
        )

        tags = [
            clean_title.lower(),
            "no copyright music",
            genre.lower(),
            "copyright free music",
            "royalty free music",
            "background music",
            "free background music",
            "no copyright background music",
            "free music",
            "youtube background music",
            "music for creators",
            "creator music",
            "gaming music",
            "gaming background music",
            "travel vlog music",
            "cinematic music",
            "cinematic background music",
            "drone footage music",
            "documentary music",
            "ai video music",
            "ai generated video music",
            "editing music",
            "video editing music",
            "montage music",
            "motivational music",
            "emotional background music",
            "deep bass music",
            "electronic music",
            "electronic background music",
            "ambient electronic music",
            "study music",
            "coding music",
            "podcast music",
            "inspirational music",
            "uplifting music",
            "dreamy music",
            "atmospheric music",
            "breakbeat music",
            f"{bpm} bpm",
            "free instrumental music",
            "royalty free soundtrack",
            "copyright safe music",
            "youtube safe music",
            "stream safe music",
            "twitch safe music",
            "viral background music",
            "trending no copyright music",
            "best no copyright music"
        ]

        return YouTubeSEOOutput(
            title=clean_title,
            alternative_titles=alt_titles,
            description=description_text,
            tags=tags,
            hashtags=hashtags,
            genre=genre,
            mood=mood,
            bpm=bpm,
            instruments=instruments,
            perfect_for=perfect_for,
            category_id="10"
        )
