import requests
import pandas as pd
import os
import time
import sys
import io
import warnings
import re
import json

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------- PATH SETUP ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- API KEYS ----------
API_KEY = os.getenv("API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: API_KEY not found", file=sys.stderr)
    sys.exit(1)

# ---------- HELPERS ----------
def extract_video_id(url_or_id):
    # Already a video ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id

    patterns = [
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?&/]+)",
        r"youtube\.com/shorts/([^?&/]+)",
        r"youtube\.com/embed/([^?&/]+)",
        r"youtube\.com/v/([^?&/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None

def get_video_metadata(video_id):
    """Fetch video metadata including title, description, views, likes, channel info"""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": API_KEY
    }
    
    response = requests.get(url, params=params, timeout=15)
    
    if response.status_code != 200:
        print(f"ERROR: Failed to fetch video metadata ({response.status_code})", file=sys.stderr)
        return None
    
    data = response.json()
    
    if not data.get("items"):
        print("ERROR: Video not found", file=sys.stderr)
        return None
    
    item = data["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]
    
    metadata = {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0))
    }
    
    return metadata
def get_gemini_summary(video_metadata):
    if not GEMINI_API_KEY:
        return "Gemini API key not configured"

    url = (
        "https://generativelanguage.googleapis.com/v1/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    prompt = f"""
Summarize this YouTube video in 10-15 sentences.

Title: {video_metadata['title']}
Channel: {video_metadata['channel_title']}
Description: {video_metadata['description'][:500]}
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            return f"Gemini API error {response.status_code}: {response.text}"

        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"Gemini exception: {str(e)}"

# def get_gemini_summary(video_metadata):
#     """Get AI-generated summary of video using Gemini API"""
#     if not GEMINI_API_KEY:
#         return "Gemini API key not configured"
    
#     try:
#         url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
#         prompt = f"""Analyze this YouTube video and provide a concise summary:

# Title: {video_metadata['title']}
# Channel: {video_metadata['channel_title']}
# Description: {video_metadata['description'][:500]}

# Provide a brief 2-3 sentence summary of what this video is about."""

#         payload = {
#             "contents": [{
#                 "parts": [{"text": prompt}]
#             }]
#         }
        
#         response = requests.post(url, json=payload, timeout=30)
        
#         if response.status_code == 200:
#             result = response.json()
#             summary = result["candidates"][0]["content"]["parts"][0]["text"]
#             return summary
#         else:
#             return f"Failed to generate summary (Status: {response.status_code})"
            
#     except Exception as e:
#         return f"Error generating summary: {str(e)}"

def fetch_youtube_comments(video_input):
    video_id = extract_video_id(video_input)

    if not video_id:
        print("ERROR: Invalid YouTube URL or ID", file=sys.stderr)
        sys.exit(1)

    # Fetch video metadata
    print("Fetching video metadata...", file=sys.stderr)
    metadata = get_video_metadata(video_id)
    
    if not metadata:
        sys.exit(1)
    
    # Get Gemini summary
    print("Generating AI summary...", file=sys.stderr)
    ai_summary = get_gemini_summary(metadata)
    
    # Print video info to stderr (for display)
    print("\n" + "="*60, file=sys.stderr)
    print(f"VIDEO: {metadata['title']}", file=sys.stderr)
    print(f"CHANNEL: {metadata['channel_title']}", file=sys.stderr)
    print(f"VIEWS: {metadata['view_count']:,}", file=sys.stderr)
    print(f"LIKES: {metadata['like_count']:,}", file=sys.stderr)
    print(f"COMMENTS: {metadata['comment_count']:,}", file=sys.stderr)
    print(f"\nAI SUMMARY:\n{ai_summary}", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)

    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    comments_data = []
    next_page = None

    print("Fetching comments...", file=sys.stderr)
    while True:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "pageToken": next_page,
            "order": "relevance",  # Get most relevant comments first
            "key": API_KEY
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code != 200:
            print(f"ERROR: YouTube API failed ({response.status_code})", file=sys.stderr)
            sys.exit(1)

        data = response.json()

        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments_data.append({
                "comment": snippet["textDisplay"],
                "author": snippet["authorDisplayName"],
                "like_count": snippet.get("likeCount", 0),
                "published_at": snippet["publishedAt"]
            })

        next_page = data.get("nextPageToken")
        if not next_page or len(comments_data) >= 500:  # Limit to 500 comments
            break

    if not comments_data:
        print("ERROR: No comments found (comments may be disabled)", file=sys.stderr)
        sys.exit(1)

    # Create DataFrame with all data
    df = pd.DataFrame(comments_data)
    
    # Sort by likes to show top comments
    df = df.sort_values("like_count", ascending=False).reset_index(drop=True)
    
    # Add video metadata to first row (for reference)
    df.attrs["metadata"] = metadata
    df.attrs["ai_summary"] = ai_summary

    # Save to CSV
    ts = time.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(DATA_DIR, f"comments_{ts}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    # Save metadata separately
    metadata_path = os.path.join(DATA_DIR, f"metadata_{ts}.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": metadata,
            "ai_summary": ai_summary
        }, f, indent=2, ensure_ascii=False)
    
    # Print top 5 most liked comments
    print("\nTOP 5 MOST LIKED COMMENTS:", file=sys.stderr)
    for idx, row in df.head(5).iterrows():
        print(f"\n[{row['like_count']} likes] {row['author']}:", file=sys.stderr)
        print(f"  {row['comment'][:100]}...", file=sys.stderr)

    # ✅ REQUIRED BY STREAMLIT
    print(csv_path)

# ---------- ENTRY ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: No video URL provided", file=sys.stderr)
        sys.exit(1)

    fetch_youtube_comments(sys.argv[1])
