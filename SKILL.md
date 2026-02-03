---
name: dy-download
description: Download Douyin (TikTok China) videos without watermark, extract audio, and perform speech-to-text transcription using Aliyun DashScope paraformer-v2 model. Use when user asks to: (1) Download a Douyin video, (2) Extract text/transcript from a Douyin video, (3) Save Douyin video with transcription, (4) Process Douyin share links. Automatically creates organized folder structure with video, audio, and markdown transcript files. Requires DASHSCOPE_API_KEY environment variable.
---

# Douyin Video Download & Transcription

Downloads Douyin videos without watermark and extracts speech-to-text using Aliyun DashScope API.

## Quick Start

Use the bundled script to download and transcribe:

```bash
python scripts/download_douyin.py "<douyin_url>"
```

## Output Structure

Creates timestamped folder in `D:\dydownload\`:

```
D:\dydownload\
└── {video_id}_{YYYYMMDD_HHMMSS}\
    ├── {video_id}.mp4     # Original video (no watermark)
    ├── {video_id}.mp3     # Extracted audio
    └── {video_id}.md      # Transcription markdown
```

## Requirements

- **Environment**: `DASHSCOPE_API_KEY` must be set
- **Python packages**: `requests`, `ffmpeg-python`, `dashscope`
- **System**: `ffmpeg` must be installed

## URL Support

Accepts any Douyin URL format:
- `https://www.douyin.com/...`
- `https://v.douyin.com/...`
- Full URLs with query parameters

## API Details

- **Service**: Aliyun DashScope (阿里云百炼)
- **Model**: paraformer-v2
- **Languages**: Chinese (zh), English (en)
- **API**: https://bailian.console.aliyun.com/
