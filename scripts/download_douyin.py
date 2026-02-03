#!/usr/bin/env python3
"""
抖音视频下载与语音转文字脚本
Download Douyin videos and extract speech-to-text using Aliyun DashScope API.
"""

import os
import re
import json
import sys
import requests
from pathlib import Path
from datetime import datetime
import dashscope
from http import HTTPStatus
from urllib import request
import ffmpeg
import argparse
from dashscope import Generation

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://www.douyin.com/'
}


def extract_video_id(share_url: str) -> str:
    """
    Extract video ID from various Douyin URL formats.

    Supports:
    - https://www.douyin.com/video/123456
    - https://www.douyin.com/...?modal_id=123456
    - Any URL with modal_id parameter
    """
    # Try to extract modal_id from URL parameters first
    modal_id_match = re.search(r'modal_id=(\d+)', share_url)
    if modal_id_match:
        return modal_id_match.group(1)

    # Try to extract video ID from path /video/123456
    video_match = re.search(r'/video/(\d+)', share_url)
    if video_match:
        return video_match.group(1)

    # Fallback: clean URL and follow redirect to get the final video ID
    try:
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', share_url)
        if urls:
            share_url_clean = urls[0]
            response = requests.get(share_url_clean, headers=HEADERS, allow_redirects=True)
            # Extract from redirected URL
            final_url = response.url.split("?")[0].strip("/")
            parts = final_url.split("/")
            if parts:
                potential_id = parts[-1]
                if potential_id.isdigit() and len(potential_id) > 10:
                    return potential_id
    except Exception:
        pass

    return None


def download_douyin_video(share_url: str, api_key: str = None) -> dict:
    """
    Download Douyin video and extract speech-to-text.

    Args:
        share_url: Douyin video share URL
        api_key: Aliyun DashScope API key (optional, uses DASHSCOPE_API_KEY env var if not provided)

    Returns:
        dict with results including folder path, files created, and transcribed text
    """
    # Get API key from parameter or environment
    if not api_key:
        api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        return {"error": "DASHSCOPE_API_KEY not set"}

    dashscope.api_key = api_key

    # Extract video ID from URL
    video_id = extract_video_id(share_url)
    if not video_id:
        return {"error": "Could not extract video ID from URL. Please provide a valid Douyin video URL."}

    share_api = f'https://www.iesdouyin.com/share/video/{video_id}'

    # Parse video info
    try:
        response = requests.get(share_api, headers=HEADERS)
        pattern = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", flags=re.DOTALL)
        find_res = pattern.search(response.text)

        if not find_res:
            return {"error": "Failed to parse video info"}

        json_data = json.loads(find_res.group(1).strip())
        VIDEO_ID_PAGE_KEY = "video_(id)/page"

        if VIDEO_ID_PAGE_KEY not in json_data.get("loaderData", {}):
            return {"error": "Video not found in API response"}

        # Safely navigate the nested structure
        loader_data = json_data["loaderData"][VIDEO_ID_PAGE_KEY]
        if "videoInfoRes" not in loader_data:
            return {"error": "videoInfoRes not found in response"}

        item_list = loader_data["videoInfoRes"].get("item_list", [])
        if not item_list:
            return {"error": "item_list is empty"}

        data = item_list[0]
        video_url = data["video"]["play_addr"]["url_list"][0].replace("playwm", "play")

    except KeyError as e:
        return {"error": f"Parse error - missing key: {str(e)}"}
    except Exception as e:
        return {"error": f"Parse error: {str(e)}"}

    # Create download folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("D:/dydownload")
    base_dir.mkdir(parents=True, exist_ok=True)

    download_dir = base_dir / f"{video_id}_{timestamp}"
    download_dir.mkdir(exist_ok=True)

    video_path = download_dir / f"{video_id}.mp4"
    audio_path = download_dir / f"{video_id}.mp3"
    md_path = download_dir / f"{video_id}.md"

    # Download video with resumable download support
    import time
    print(f"Downloading video to: {video_path}")
    max_retries = 10
    session = requests.Session()
    session.headers.update(HEADERS)

    downloaded_size = 0
    if video_path.exists():
        downloaded_size = video_path.stat().st_size

    for attempt in range(max_retries):
        try:
            # Re-fetch video URL for each attempt
            if attempt > 0 or downloaded_size > 0:
                print(f"Fetching video URL...")
                share_api = f'https://www.iesdouyin.com/share/video/{video_id}'
                resp = session.get(share_api, timeout=30)
                pattern = re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", flags=re.DOTALL)
                find_res = pattern.search(resp.text)
                if find_res:
                    json_data = json.loads(find_res.group(1).strip())
                    loader_data = json_data["loaderData"]["video_(id)/page"]
                    item_list = loader_data["videoInfoRes"].get("item_list", [])
                    if item_list:
                        video_url = item_list[0]["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
                if attempt > 0:
                    time.sleep(2)

            # Resume download with Range header
            headers_range = HEADERS.copy()
            if downloaded_size > 0:
                headers_range['Range'] = f'bytes={downloaded_size}-'
                print(f"Resuming from {downloaded_size / 1024 / 1024:.1f} MB...")

            response = session.get(video_url, headers=headers_range, stream=True, timeout=(30, 120))
            response.raise_for_status()

            mode = 'ab' if downloaded_size > 0 else 'wb'
            with open(video_path, mode) as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if downloaded_size % (1024 * 1024) == 0:
                            print(f"Downloaded: {downloaded_size / 1024 / 1024:.1f} MB", end='\r')
            print()  # New line after progress

            # Verify download completed
            if video_path.stat().st_size < 1024 * 1024:
                raise Exception("Downloaded file too small, may be incomplete")

            break
        except (requests.exceptions.RequestException, OSError, Exception) as e:
            print(f"\nDownload interrupted at {downloaded_size / 1024 / 1024:.1f} MB: {e}")
            if downloaded_size > 0:
                print(f"Partial file saved, will resume...")
            if attempt == max_retries - 1:
                if video_path.exists() and video_path.stat().st_size > 10 * 1024 * 1024:
                    print(f"Warning: Download incomplete but {video_path.stat().st_size / 1024 / 1024:.1f} MB saved")
                    break  # Keep partial file if > 10MB
                return {"error": f"Video download failed after {max_retries} attempts: {str(e)}"}
            print(f"Retrying ({attempt + 1}/{max_retries})...")
            continue
    video_size_mb = video_path.stat().st_size / 1024 / 1024
    print(f"Video downloaded: {video_size_mb:.2f} MB")

    # Extract audio
    print(f"Extracting audio to: {audio_path}")
    try:
        (
            ffmpeg
            .input(str(video_path))
            .output(str(audio_path), acodec='libmp3lame', audio_bitrate='64k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        audio_size_mb = audio_path.stat().st_size / 1024 / 1024
        print(f"Audio extracted: {audio_size_mb:.2f} MB")
    except Exception as e:
        return {"error": f"Audio extraction failed: {str(e)}"}

    # Transcribe using DashScope
    transcribed_text = ""
    try:
        print("Starting speech-to-text transcription...")
        task_response = dashscope.audio.asr.Transcription.async_call(
            model='paraformer-v2',
            file_urls=[video_url],
            language_hints=['zh', 'en']
        )

        print(f"Task ID: {task_response.output.task_id}")
        print("Waiting for transcription to complete...")

        transcription_response = dashscope.audio.asr.Transcription.wait(
            task=task_response.output.task_id
        )

        if transcription_response.status_code == HTTPStatus.OK:
            for transcription in transcription_response.output['results']:
                result_url = transcription['transcription_url']
                result = json.loads(request.urlopen(result_url).read().decode('utf8'))

                if 'transcripts' in result and len(result['transcripts']) > 0:
                    transcribed_text = result['transcripts'][0]['text']
                else:
                    transcribed_text = "No text recognized"
        else:
            transcribed_text = f"Transcription failed: {transcription_response.output.message}"

    except Exception as e:
        transcribed_text = f"Transcription error: {str(e)}"

    # Generate content summary using AI
    content_summary = ""
    if transcribed_text and len(transcribed_text) > 100:
        try:
            print("Generating content summary...")
            summary_prompt = f"""请分析以下视频转录文本，生成一个结构化的内容概要。

要求：
1. 提取视频的核心主题
2. 总结3-5个关键要点，每个要点用简短的标题和一句话描述
3. 提取2-3个最有价值的金句或核心观点
4. 使用markdown格式，保持简洁明了

转录文本：
{transcribed_text[:4000]}

请以"## 视频内容概要"开头，生成结构化的概要："""

            response = Generation.call(
                model='qwen-plus',
                prompt=summary_prompt,
                max_tokens=1500,
                temperature=0.7
            )

            if response.status_code == 200:
                content_summary = response.output.text.strip()
                print("Content summary generated successfully!")
            else:
                print(f"Summary generation warning: {response.message}")
        except Exception as e:
            print(f"Summary generation error: {str(e)}")

    # Save MD file
    print(f"Saving transcription to: {md_path}")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# 抖音视频语音转文字\n\n")
        f.write(f"视频ID: {video_id}\n")
        f.write(f"下载时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Write AI-generated summary if available
        if content_summary:
            f.write(f"{content_summary}\n\n")
            f.write(f"---\n\n")

        f.write(f"## 完整转录内容\n\n")
        f.write(transcribed_text)

    print(f"\n完成! 文件夹: {download_dir}")
    print(f"  - 视频: {video_path.name} ({video_size_mb:.2f} MB)")
    print(f"  - 音频: {audio_path.name} ({audio_size_mb:.2f} MB)")
    print(f"  - 文字: {md_path.name}")

    return {
        "success": True,
        "video_id": video_id,
        "folder": str(download_dir),
        "files": {
            "video": str(video_path),
            "audio": str(audio_path),
            "transcript": str(md_path)
        },
        "transcribed_text": transcribed_text
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Download Douyin videos and extract speech-to-text using Aliyun DashScope API.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_douyin.py "https://www.douyin.com/video/7586019227824934201"
  python download_douyin.py "https://www.douyin.com/...?modal_id=7586019227824934201" --api-key sk-xxxxx
  python download_douyin.py "https://v.douyin.com/xxxxx"

Note: Set DASHSCOPE_API_KEY environment variable or use --api-key parameter.
Get API key from: https://bailian.console.aliyun.com/
        """
    )
    parser.add_argument('url', help='Douyin video URL')
    parser.add_argument('--api-key', '-k', help='Aliyun DashScope API key (overrides DASHSCOPE_API_KEY env var)')

    args = parser.parse_args()

    result = download_douyin_video(args.url, api_key=args.api_key)

    if result.get("success"):
        print("\n=== SUCCESS ===")
        print(f"Folder: {result['folder']}")
        print(f"\nTranscription preview:")
        print(result['transcribed_text'][:500] + "..." if len(result['transcribed_text']) > 500 else result['transcribed_text'])
    else:
        print(f"\n=== ERROR: {result.get('error', 'Unknown error')} ===")
        sys.exit(1)
