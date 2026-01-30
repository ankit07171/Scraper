
import sys

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





import requests
import pandas as pd
import os
import time
import sys
import io
import re
import warnings
from dotenv import load_dotenv 
load_dotenv()   # 👈 THIS IS REQUIRED

API_KEY = os.getenv("API_KEY")

warnings.filterwarnings("ignore")
# import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# API_KEY = ""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def extract_video_id(url_or_id):
    if "youtube.com" in url_or_id:
        return url_or_id.split("v=")[-1].split("&")[0]
    if "youtu.be" in url_or_id:
        return url_or_id.split("/")[-1]
    return url_or_id.strip()

def fetch_youtube_comments(video_input):
    video_id = extract_video_id(video_input)

    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": 100,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    comments = [
        item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        for item in data.get("items", [])
    ]

    if not comments:
        print("")  # IMPORTANT: print NOTHING
        sys.exit(0)

    df = pd.DataFrame({"comment": comments})

    ts = time.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(DATA_DIR, f"comments_{ts}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # 🔥 ONLY print CSV path
    print(csv_path)

if __name__ == "__main__":
    fetch_youtube_comments(sys.argv[1])
