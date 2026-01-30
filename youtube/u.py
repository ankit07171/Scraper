# import requests

# API_KEY = "AIzaSyBqKKezsIqOPpwh6CsInrs8yVnr2sOPdiI"
# VIDEO_ID = "7YieHcRLFmg"

# url = "https://www.googleapis.com/youtube/v3/commentThreads"

# params = {
#     "part": "snippet",
#     "videoId": VIDEO_ID,
#     "maxResults": 100,
#     "key": API_KEY
# }

# response = requests.get(url, params=params)
# data = response.json()

# for item in data["items"]:
#     comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
#     author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
#     print(author, ":", comment)


# import requests
# import pandas as pd
# import os
# import time
# import sys, io

# # ---------------- UTF-8 for Windows console ----------------
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API_KEY = "AIzaSyBqKKezsIqOPpwh6CsInrs8yVnr2sOPdiI"  # Add your YouTube Data API v3 key

# def fetch_youtube_comments(video_id):
#     url = "https://www.googleapis.com/youtube/v3/commentThreads"
#     params = {
#         "part": "snippet",
#         "videoId": video_id,
#         "maxResults": 100,
#         "key": API_KEY
#     }

#     response = requests.get(url, params=params)
#     data = response.json()

#     comments = []
#     for item in data.get("items", []):
#         text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
#         comments.append(text)

#     if comments:
#         df = pd.DataFrame({"comment": comments})
#         os.makedirs("data", exist_ok=True)
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         csv_path = os.path.join("data", f"comments_{timestamp}.csv")
#         df.to_csv(csv_path, index=False, encoding='utf-8-sig')

#         print(csv_path)  # Streamlit will read this path
#         print(f"Saved {len(comments)} YouTube comments")
#         return df
#     else:
#         print("No comments found")
#         return pd.DataFrame()

# # ---------------- USAGE ----------------
# if __name__ == "__main__":
#     video_id = sys.argv[1]  # Streamlit passes Video ID
#     fetch_youtube_comments(video_id)



# import requests
# import pandas as pd
# import os
# import time
# import sys
# import io
# import re
# import warnings

# warnings.filterwarnings("ignore")
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# # ---------- PATH SETUP ----------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(BASE_DIR, "data")
# os.makedirs(DATA_DIR, exist_ok=True)

# # ---------- API KEY ----------
# API_KEY = os.getenv("API_KEY")

# if not API_KEY:
#     print("ERROR: API_KEY not found", file=sys.stderr)
#     sys.exit(1)

# # ---------- HELPERS ----------
# def extract_video_id(url_or_id):
#     # Already a video ID
#     if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
#         return url_or_id

#     patterns = [
#         r"youtube\.com/watch\?v=([^&]+)",
#         r"youtu\.be/([^?&/]+)",
#         r"youtube\.com/shorts/([^?&/]+)",
#         r"youtube\.com/embed/([^?&/]+)",
#         r"youtube\.com/v/([^?&/]+)",
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, url_or_id)
#         if match:
#             return match.group(1)

#     return None

# def fetch_youtube_comments(video_input):
#     video_id = extract_video_id(video_input)

#     url = "https://www.googleapis.com/youtube/v3/commentThreads"
#     params = {
#         "part": "snippet",
#         "videoId": video_id,
#         "maxResults": 100,
#         "key": API_KEY
#     }

#     response = requests.get(url, params=params, timeout=15)

#     if response.status_code != 200:
#         print(f"ERROR: YouTube API failed ({response.status_code})", file=sys.stderr)
#         sys.exit(1)

#     data = response.json()

#     comments = [
#         item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
#         for item in data.get("items", [])
#     ]

#     if not comments:
#         print("ERROR: No comments found", file=sys.stderr)
#         sys.exit(1)

#     df = pd.DataFrame({"comment": comments})

#     ts = time.strftime("%Y%m%d_%H%M%S")
#     csv_path = os.path.join(DATA_DIR, f"comments_{ts}.csv")
#     df.to_csv(csv_path, index=False, encoding="utf-8-sig")

#     # ✅ ONLY OUTPUT — REQUIRED BY STREAMLIT
#     print(csv_path)

# # ---------- ENTRY ----------
# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("ERROR: No video URL provided", file=sys.stderr)
#         sys.exit(1)

#     fetch_youtube_comments(sys.argv[1])




import requests
import pandas as pd
import os
import time
import sys
import io
import warnings
import re   # ✅ FIX 1

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------- PATH SETUP ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- API KEY ----------
API_KEY = os.getenv("API_KEY")

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
        r"youtube\.com/shorts/([^?&/]+)",   # ✅ Shorts supported
        r"youtube\.com/embed/([^?&/]+)",
        r"youtube\.com/v/([^?&/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    return None

def fetch_youtube_comments(video_input):
    video_id = extract_video_id(video_input)

    if not video_id:
        print("ERROR: Invalid YouTube URL or ID", file=sys.stderr)
        sys.exit(1)

    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    comments = []
    next_page = None

    while True:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": 100,
            "pageToken": next_page,
            "key": API_KEY
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code != 200:
            print(f"ERROR: YouTube API failed ({response.status_code})", file=sys.stderr)
            sys.exit(1)

        data = response.json()

        for item in data.get("items", []):
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

        next_page = data.get("nextPageToken")
        if not next_page:
            break

    if not comments:
        print("ERROR: No comments found (comments may be disabled)", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame({"comment": comments})

    ts = time.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(DATA_DIR, f"comments_{ts}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # ✅ REQUIRED BY STREAMLIT
    print(csv_path)

# ---------- ENTRY ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: No video URL provided", file=sys.stderr)
        sys.exit(1)

    fetch_youtube_comments(sys.argv[1])
