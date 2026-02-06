import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import glob
import sys

from dotenv import load_dotenv
load_dotenv()

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)
sys.path.insert(0, SRC_DIR)

from preprocess import clean_text
from classifier import classify_comment
from simi import spam_similarity_score
from burst import burst_detect
from score import campaign_score, explain_campaign

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Social Media Comment Analyzer",
    page_icon="📊",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "csv_path" not in st.session_state:
    st.session_state.csv_path = None
if "df" not in st.session_state:
    st.session_state.df = None

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align:center;'>📊 Social Media Comment Analyzer</h1>
    <p style='text-align:center;'>YouTube & Instagram Spam + Campaign Detection</p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- INPUT SECTION ----------------
st.subheader("📌 Select Platform")
platform = st.selectbox("Platform", ["Select", "YouTube", "Instagram"])

st.subheader("🔗 Enter URL / ID")
url = st.text_input(
    "Video / Reel URL",
    placeholder="YouTube video ID / URL OR Instagram Reel URL"
)

# ---------------- FETCH BUTTON ----------------
if st.button("🚀 Fetch & Analyze"):
    if platform == "Select":
        st.warning("Please select a platform")
        st.stop()
    if not url:
        st.warning("Please enter a valid URL")
        st.stop()

    with st.spinner("Fetching comments..."):
        if platform == "YouTube":
            result = subprocess.run(
                ["python", "youtube/u.py", url],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
        else:
            result = subprocess.run(
                [sys.executable, "insta/i.py", "--url", url],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                env=os.environ
            )

        csv_path = None
        for line in result.stdout.splitlines():
            if line.endswith(".csv") and os.path.exists(line):
                csv_path = line
                break

        if not csv_path:
            st.error("No CSV generated")
            st.stop()

        st.session_state.csv_path = csv_path
        st.session_state.df = pd.read_csv(csv_path)
        st.success(f"Loaded {len(st.session_state.df)} comments")

# ---------------- LOAD PREVIOUS DATA ----------------
csv_files = sorted(glob.glob(os.path.join(DATA_DIR, "comments_*.csv")), reverse=True)
if csv_files:
    selected = st.selectbox("📂 Load Existing Dataset", csv_files)
    if selected != st.session_state.csv_path:
        st.session_state.csv_path = selected
        st.session_state.df = pd.read_csv(selected)

# ---------------- ANALYSIS ----------------
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    df["comment"] = df["comment"].astype(str)

    if "category" not in df.columns:
        df["cleaned"] = df["comment"].apply(clean_text)
        df["category"] = df["cleaned"].apply(classify_comment)

    spam_texts = df[df["category"] == "Spam"]["cleaned"].tolist()
    similarity_score, spam_clusters = spam_similarity_score(spam_texts)

    burst_flag, burst_series = burst_detect(
        df.get("published_at", pd.Series([None]*len(df)))
    )

    spam_ratio = (df["category"] == "Spam").mean()
    risk_score = campaign_score(similarity_score, burst_flag, spam_ratio)
    reasons = explain_campaign(similarity_score, burst_flag, spam_ratio)

    df["category"] = df["category"].str.capitalize()

    # ---------------- SIGNALS ----------------
    st.markdown("---")
    st.subheader("🔍 Campaign Signals")
    st.write(f"- **Spam Ratio:** {spam_ratio:.2%}")
    st.write(f"- **Similarity Score:** {similarity_score}")
    st.write(f"- **Burst Detected:** {'Yes' if burst_flag else 'No'}")

    # ---------------- CLUSTERS ----------------
    st.markdown("---")
    st.subheader("🧩 Repeated Spam Clusters")
    if spam_clusters:
        for i, cluster in enumerate(spam_clusters, 1):
            with st.expander(f"Cluster {i} • {len(cluster)} comments"):
                for idx in cluster[:5]:
                    st.write("•", spam_texts[idx])
    else:
        st.success("No repeated spam patterns found")

    # ---------------- METRICS ----------------
    st.markdown("---")
    st.subheader("📈 Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("Positive 😊", (df["category"] == "Positive").sum())
    c3.metric("Neutral 😐", (df["category"] == "Neutral").sum())
    c4.metric("Spam 🚫", (df["category"] == "Spam").sum())

    # ---------------- RISK ----------------
    st.markdown("---")
    st.subheader("🚨 Campaign Risk Score")
    st.metric("Risk Score", f"{risk_score} / 100")
    if reasons:
        for r in reasons:
            st.warning(r)
    else:
        st.success("No coordinated campaign detected")

    # ---------------- TIMELINE ----------------
    if burst_series is not None:
        st.markdown("---")
        st.subheader("⏱ Comment Activity Timeline")
        fig, ax = plt.subplots()
        burst_series.plot(ax=ax)
        st.pyplot(fig)

    # ---------------- CHARTS ----------------
    st.markdown("---")
    st.subheader("📊 Comment Distribution")
    counts = df["category"].value_counts()

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        counts.plot(kind="pie", autopct="%1.1f%%", ax=ax)
        st.pyplot(fig)

    # ---------------- TABLE ----------------
    st.markdown("---")
    st.subheader("🗂 Filter Comments")
    cat = st.selectbox("Category", sorted(df["category"].unique()))
    st.dataframe(df[df["category"] == cat][["comment", "category"]])

    st.download_button(
        "📥 Download CSV",
        df.to_csv(index=False),
        "classified_comments.csv",
        "text/csv"
    )

else:
    st.info("Select platform and fetch comments to start analysis")
