# 🎵 YouTube Music Channel Automation Agent

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-3_Pro-orange?logo=google)
![YouTube API](https://img.shields.io/badge/YouTube_API-v3-red?logo=youtube)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade, 100% free Python application designed to completely automate YouTube music channel publishing workflows. The application generates or accepts audio files, renders crisp 1080p MP4 videos, produces SEO-optimized metadata (titles, structured descriptions, hashtags, and keywords blocks) via **Gemini 3 Pro**, extracts custom **middle-frame keyframe thumbnails** via **OpenCV**, and publishes directly to YouTube using **YouTube Data API v3**.

---

## 🎯 Key Features

- 🎧 **Audio & Music Management**: Integrated with APIMart / Google Cloud Lyria REST APIs and includes a zero-downtime synthetic audio generator for offline execution.
- 🎬 **1080p Video Creation Engine**: Local high-efficiency rendering using **MoviePy** & **FFmpeg** to overlay audio tracks onto customizable background graphic templates.
- 🤖 **Gemini 3 Pro SEO Agent**: Generates structured YouTube metadata following an industry-standard reference layout:
  - Engaging intro paragraph
  - Alternative keyword titles (3-5 variations)
  - Track information (Genre, Mood, BPM)
  - Featured instruments breakdown
  - Recommended content use-cases ("Perfect For")
  - Creator license & credit format
  - Auto-generated video chapters/timestamps
  - Hashtags block (`#NoCopyrightMusic...`)
  - Comprehensive **SEO Keywords** block
- 🖼️ **Smart Middle-Frame Thumbnail Extractor**: Uses **OpenCV** & **Pillow** to calculate and extract the exact middle frame (`duration / 2.0`) of the video, ensuring track title graphics and visualizers are rendered at full opacity.
- 🚀 **YouTube Data API v3 Publisher**: Direct video and thumbnail publisher featuring resumable chunked upload protocols (`MediaFileUpload`) and auto-refreshing OAuth 2.0 token management.
- 📦 **Batch Folder Publisher**: Effortlessly batch-process and publish an entire folder of videos or `.mp3`/`.wav` audio tracks sequentially in a single CLI command.
- 💰 **100% Free**: Operates fully within Google AI Studio free tier rate limits and YouTube's 10,000 daily free API quota.

---

## 🏗️ System Architecture

```
[ User Audio/Video Input ]
           │
           ▼
  ┌─────────────────┐
  │ Video Engine    │ ── (Converts .mp3/.wav to 1080p MP4 via MoviePy/FFmpeg)
  └────────┬────────┘
           │
           ├───────────────────────────────┐
           ▼                               ▼
  ┌─────────────────┐             ┌─────────────────┐
  │ Gemini SEO Agent│             │ Thumbnail Engine│
  │ (Description,   │             │ (Extracts exact │
  │  Tags, Keywords)│             │  middle frame)  │
  └────────┬────────┘             └────────┬────────┘
           │                               │
           └───────────────┬───────────────┘
                           ▼
              ┌────────────────────────┐
              │ YouTube Data API v3    │
              │ Resumable Uploader     │
              └────────────┬───────────┘
                           ▼
               [ Live YouTube Video ]
```

---

## 📁 Repository Structure

```
youtube_music_automation/
├── config/
│   └── settings.py              # Pydantic configuration settings
├── music/
│   ├── base.py                  # Abstract base music generator interface
│   ├── flow_music.py            # APIMart Flow Music & Fallback wave generator
│   └── manager.py               # Audio verification & track manager
├── video/
│   └── ffmpeg_engine.py         # MoviePy & FFmpeg 1080p video creator
├── seo/
│   ├── schemas.py               # YouTubeSEOOutput Pydantic schema
│   └── gemini_agent.py          # Gemini 3 Pro SEO metadata agent
├── thumbnail/
│   └── extractor.py             # OpenCV middle-frame keyframe thumbnail extractor
├── youtube/
│   ├── auth.py                  # Resilient OAuth 2.0 flow helper
│   └── uploader.py              # Resumable video & thumbnail uploader
└── pipeline.py                  # Master PublishingPipeline orchestrator

cli.py                           # Command Line Interface (CLI)
main.py                          # Sample pipeline runner script
scheduler.py                     # Automated background job scheduler (APScheduler)
requirements.txt                 # Project dependencies
```

---

## ⚙️ Prerequisites & Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/K-Sricharan/Youtube-Automation.git
cd Youtube-Automation
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-pro
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_TOKEN_FILE=token.json
YOUTUBE_PRIVACY_STATUS=public
```
*(Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/)).*

### 3. Setup YouTube Data API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **YouTube Data API v3**.
3. Go to **OAuth consent screen** → Add your email address under **Test Users**.
4. Go to **Credentials** → **+ Create Credentials** → **OAuth client ID** → Select **Desktop App**.
5. Click **Download JSON**, save it to the root directory as `client_secrets.json`.

---

## 🚀 Usage Guide

### 🎥 Upload a Single Video or Audio File
```bash
python cli.py upload-video --video "path/to/track.mp4" --title "Midnight Velocity | Drift Phonk" --genre "Drift Phonk" --privacy public
```
*(Note: If you supply an `.mp3` or `.wav` file, the app automatically renders it into a 1080p MP4 video first!)*

### 📂 Batch Upload an Entire Folder (e.g., 5 Files at Once)
```bash
python cli.py upload-folder --folder "path/to/music_folder" --genre "Future Bass" --privacy public
```

### 🏷️ Generate SEO Metadata Only
```bash
python cli.py seo-only --prompt "Crystal Horizon" --genre "Liquid Drum & Bass"
```

### 🔄 Run Full End-to-End Synthetic Pipeline
```bash
python main.py
```

---

## 💰 Free Tier & Quota Safety

- **Google Gemini API**: 100% Free (1,500 free requests/day vs 1 request needed per upload).
- **YouTube Data API v3**: 100% Free (10,000 units/day quota allows ~6 full video uploads/day).
- **Local Rendering**: Uses local CPU via FFmpeg/MoviePy ($0 cloud cost).

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
