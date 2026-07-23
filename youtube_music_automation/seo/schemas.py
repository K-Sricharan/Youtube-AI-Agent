from typing import List, Optional
from pydantic import BaseModel, Field

class YouTubeSEOOutput(BaseModel):
    """Pydantic structured output schema for YouTube SEO metadata following creator template reference."""
    title: str = Field(
        ...,
        description="Main catchy YouTube video title (< 100 characters)."
    )
    alternative_titles: List[str] = Field(
        default_factory=list,
        description="List of 3-5 keyword-rich alternative titles for SEO reference."
    )
    description: str = Field(
        ...,
        description="Comprehensive structured video description following creator reference template."
    )
    tags: List[str] = Field(
        ...,
        description="List of 20 to 40 highly relevant YouTube search tags."
    )
    hashtags: List[str] = Field(
        ...,
        description="List of 10 to 15 trending hashtags starting with '#'."
    )
    genre: str = Field(
        default="Liquid Drum & Bass",
        description="The primary musical genre."
    )
    mood: str = Field(
        default="Emotional • Atmospheric • Inspiring",
        description="The emotional mood/vibe of the track."
    )
    bpm: Optional[int] = Field(
        default=174,
        description="Beats per minute (BPM) of the track."
    )
    instruments: List[str] = Field(
        default_factory=list,
        description="List of instruments featured in the track."
    )
    perfect_for: List[str] = Field(
        default_factory=list,
        description="List of content types/use cases this music is perfect for."
    )
    category_id: str = Field(
        default="10",
        description="YouTube category ID (10 represents Music)."
    )
