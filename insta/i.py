# from apify_client import ApifyClient
# import pandas as pd
# import time, os, argparse, sys, io

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# def scrape_instagram(reel_url, token):
#     if not token or not token.strip():
#         print("ERROR: Empty APIFY token", file=sys.stderr)
#         sys.exit(1)

#     client = ApifyClient(token)
#     comments = []

#     run = client.actor("apify/instagram-comment-scraper").call(
#         run_input={
#             "directUrls": [reel_url],
#             "maxRequestsPerCrawl": 1,
#             "maxComments": 100
#         }
#     )

#     while True:
#         status = client.run(run["id"]).get()["status"]
#         if status in ("SUCCEEDED", "FAILED"):
#             break
#         time.sleep(5)
#         print(f"Status: {status}", file=sys.stderr)

#     if status != "SUCCEEDED":
#         print(f"Run failed: {status}", file=sys.stderr)
#         sys.exit(1)

#     dataset = client.dataset(run["defaultDatasetId"]).list_items().items
#     for item in dataset:
#         if item.get("text"):
#             comments.append(item["text"].strip())

#     if not comments:
#         print("No comments found", file=sys.stderr)
#         sys.exit(1)

#     df = pd.DataFrame({"comment": comments})

#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     DATA_DIR = os.path.join(BASE_DIR, "../data")
#     os.makedirs(DATA_DIR, exist_ok=True)

#     ts = time.strftime("%Y%m%d_%H%M%S")
#     csv_path = os.path.abspath(os.path.join(DATA_DIR, f"comments_{ts}.csv"))

#     df.to_csv(csv_path, index=False, encoding="utf-8-sig")
#     print(csv_path)  # ONLY stdout

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     # parser.add_argument("--url", required=True)
#     args = parser.parse_args()
#     print(args)
#     print(args.url)
#     APIFY_TOKEN = os.getenv("")
#     scrape_instagram(args.url, APIFY_TOKEN)

 
import pandas as pd
import time, os, argparse, sys, io 
from apify_client import ApifyClient
import sys
import os 

from dotenv import load_dotenv 
load_dotenv()   # 👈 THIS IS REQUIRED

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
print(APIFY_TOKEN)  # temporary debug

# UTF-8 output (Windows fix)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def scrape_instagram(reel_url, token):
    if not token:
        print("ERROR: APIFY_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(token)

    run = client.actor("apify/instagram-comment-scraper").call(
        run_input={
            "directUrls": [reel_url],
            "maxComments": 100
        }
    )

    # Wait until finished
    while True:
        status = client.run(run["id"]).get()["status"]
        if status in ("SUCCEEDED", "FAILED"):
            break
        time.sleep(3)

    if status != "SUCCEEDED":
        print("ERROR: Instagram scrape failed", file=sys.stderr)
        sys.exit(1)

    dataset = client.dataset(run["defaultDatasetId"]).list_items().items
    comments = [item["text"] for item in dataset if item.get("text")]

    if not comments:
        print("ERROR: No comments found", file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame({"comment": comments})

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../data")
    os.makedirs(DATA_DIR, exist_ok=True)

    ts = time.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.abspath(os.path.join(DATA_DIR, f"comments_{ts}.csv"))

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(csv_path)  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN env var missing", file=sys.stderr)
        sys.exit(1) 
    scrape_instagram(args.url, APIFY_TOKEN)
