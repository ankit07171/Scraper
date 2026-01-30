import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import glob
import sys

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)
sys.path.insert(0, SRC_DIR)

from preprocess import clean_text
from classifier import classify_comment


st.set_page_config(
    page_title="Social Media Comment Analyzer",
    page_icon="📊",
    layout="wide"
)


if "csv_path" not in st.session_state:
    st.session_state.csv_path = None

if "df" not in st.session_state:
    st.session_state.df = None

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align: center;'>📊 Social Media Comment Analyzer</h1>
    <p style='text-align: center;'>Analyze YouTube & Instagram comments using NLP</p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

st.subheader("📌 Select Platform")
platform = st.selectbox(
    "Platform",
    ["Select", "YouTube", "Instagram"]
)


st.subheader("🔗 Enter URL / ID")

if platform == "YouTube":
    url = st.text_input(
        "YouTube Video URL or ID",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID or VIDEO_ID"
    )
elif platform == "Instagram":
    url = st.text_input(
        "Instagram Reel URL",
        placeholder="https://www.instagram.com/reel/..."
    )
else:
    url = ""

result = None   # 👈 ADD THIS BEFORE st.button

if st.button("🚀 Fetch & Analyze"):
    if platform == "Select":
        st.warning("⚠️ Please select a platform")
        st.stop()

    if not url:
        st.warning("⚠️ Please enter a valid URL / ID")
        st.stop()

    with st.spinner("⏳ Fetching comments..."):
        if platform == "YouTube":
            result = subprocess.run(
                ["python", "youtube/u.py", url],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
        elif platform == "Instagram":
            python_exe = sys.executable
            env = os.environ.copy()
            env["APIFY_TOKEN"] = os.getenv("APIFY_TOKEN")
           
            # if not env["APIFY_TOKEN"] :
            #     st.error("❌ APIFY_TOKEN not found in .env")
            #     st.stop()
            result = subprocess.run(
                [python_exe, "insta/i.py", "--url", url],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                env=env    
                )
            if result is not None:
                st.code(result.stdout or "NO STDOUT", language="text")
                st.code(result.stderr or "NO STDERR", language="text")

        # elif platform == "Instagram":
            # python_exe = sys.executable
            # env = os.environ.copy()
            # env["APIFY_TOKEN"] = os.getenv("APIFY_TOKEN")
            # if not env["APIFY_TOKEN"]:
            #     st.error("APIFY_TOKEN not found")
            #     st.stop()
            #     result = subprocess.run(
            #         [python_exe, "insta/i.py", "--url", url],
            #         capture_output=True,
            #         text=True,
            #         cwd=BASE_DIR,
            #         env=env
            #     )
            
            # if result is not None:
            #     st.code(result.stdout or "NO STDOUT", language="text")
            #     st.code(result.stderr or "NO STDERR", language="text")

        csv_path = None
        if result is None or not result.stdout:
            st.error("❌ Script did not return any output")
            st.stop()
            
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.endswith(".csv") and os.path.exists(line):
                csv_path = line
                break

        if not csv_path:
            st.error("❌ No comments found or CSV not created")
            st.stop()

        st.session_state.csv_path = csv_path
        st.session_state.df = pd.read_csv(csv_path)

        st.success(f"✅ Loaded {len(st.session_state.df)} comments")

# ---------------- LOAD PREVIOUS CSV ----------------
all_csv_files = sorted(
    glob.glob(os.path.join(DATA_DIR, "comments_*.csv")),
    reverse=True
)

if all_csv_files:
    selected_csv = st.selectbox(
        "📂 Select existing dataset",
        all_csv_files
    )

    if st.session_state.csv_path != selected_csv:
        st.session_state.csv_path = selected_csv
        st.session_state.df = pd.read_csv(selected_csv)

# ---------------- ANALYSIS ----------------
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    df["comment"] = df["comment"].astype(str)

    if "category" not in df.columns:
        df["cleaned"] = df["comment"].apply(clean_text)
        df["category"] = df["cleaned"].apply(classify_comment)

    df["category"] = df["category"].str.capitalize()

    st.markdown("---")

    # ---------------- METRICS ----------------
    st.subheader("📈 Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df))
    col2.metric("Positive 😊", (df["category"] == "Positive").sum())
    col3.metric("Neutral 😐", (df["category"] == "Neutral").sum())
    col4.metric("Spam 🚫", (df["category"] == "Spam").sum())

    # ---------------- CHARTS ----------------
    st.subheader("📊 Comment Distribution")
    counts = df["category"].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        counts.plot(kind="bar", ax=ax1)
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        counts.plot(kind="pie", autopct="%1.1f%%", ax=ax2)
        ax2.set_ylabel("")
        st.pyplot(fig2)

    # ---------------- CATEGORY FILTER (AFTER GRAPHS) ----------------
    st.markdown("---")
    st.subheader("🗂 View Comments by Category")

    categories = sorted(df["category"].unique())
    selected_category = st.selectbox("Select Category", categories)

    filtered_df = df[df["category"] == selected_category]

    st.write(f"Showing **{len(filtered_df)}** comments")

    st.dataframe(
        filtered_df[["comment", "category"]],
        width="stretch"
    )


    st.download_button(
        "📥 Download Classified CSV",
        df.to_csv(index=False),
        "classified_comments.csv",
        "text/csv"
    )

else:
    st.info("📂 Select a platform, enter URL, and click Fetch & Analyze")