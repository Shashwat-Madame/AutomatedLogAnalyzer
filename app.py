from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analyzer import analyze_logs, get_summary, create_text_report

st.set_page_config(
    page_title="Automated Log File Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Automated Log File Analyzer")
st.caption("Analyze system logs, identify issues, and generate reports.")

st.sidebar.header("Log File")
source = st.sidebar.radio(
    "Choose input source",
    ["Use sample.log", "Upload a log file"],
)

filename = ""
log_text = ""

if source == "Use sample.log":
    sample_path = Path(__file__).with_name("sample.log")
    try:
        log_text = sample_path.read_text(encoding="utf-8")
        filename = sample_path.name
    except FileNotFoundError:
        st.error("sample.log was not found in the project folder.")
        st.stop()
else:
    uploaded_file = st.sidebar.file_uploader(
        "Choose a .log or .txt file",
        type=["log", "txt"],
    )
    if uploaded_file is None:
        st.info("Upload a log file from the sidebar to begin.")
        st.stop()

    log_text = uploaded_file.getvalue().decode("utf-8", errors="replace")
    filename = uploaded_file.name

st.subheader(f"Analysis Results: {filename}")
df = analyze_logs(log_text)
summary = get_summary(df)

if df.empty:
    st.warning("No log entries found. The file may be empty.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Entries", summary["total"])
col2.metric("Critical", summary["critical"])
col3.metric("Errors", summary["errors"])
col4.metric("Warnings", summary["warnings"])

col5, col6, col7 = st.columns(3)
col5.metric("Information", summary["info"])
col6.metric("Debug", summary["debug"])
col7.metric("Unrecognized", summary["unknown"])

if summary["critical"] > 0:
    st.error("Overall Status: Critical issues detected.")
elif summary["errors"] > 0:
    st.warning("Overall Status: Errors detected.")
elif summary["warnings"] > 0:
    st.warning("Overall Status: Warnings detected.")
else:
    st.success("Overall Status: No errors or warnings detected.")

st.subheader("Log Statistics")
left, right = st.columns(2)

level_counts = (
    df["Level"].value_counts().rename_axis("Level").reset_index(name="Count")
)
with left:
    fig = px.bar(
        level_counts, x="Level", y="Count", color="Level",
        title="Frequency of Log Levels",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    severity_counts = (
        df["Severity"].value_counts().rename_axis("Severity")
        .reset_index(name="Count")
    )
    fig = px.pie(
        severity_counts, names="Severity", values="Count",
        title="Distribution by Severity",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Most Frequent Issues")
issues = df[df["Level"].isin(["CRITICAL", "ERROR", "WARNING"])]
if issues.empty:
    st.info("No critical events, errors, or warnings found.")
else:
    frequent = (
        issues.groupby(["Level", "Message"]).size()
        .reset_index(name="Occurrences")
        .sort_values("Occurrences", ascending=False)
        .head(10)
    )
    st.dataframe(frequent, use_container_width=True, hide_index=True)

st.subheader("Detailed Log Entries")
available_levels = sorted(df["Level"].unique().tolist())
selected_levels = st.multiselect(
    "Filter by log level", options=available_levels, default=available_levels
)
search_text = st.text_input(
    "Search log messages", placeholder="Enter a keyword, e.g. database"
)

filtered_df = df[df["Level"].isin(selected_levels)]
if search_text.strip():
    filtered_df = filtered_df[
        filtered_df["Original Log"].str.contains(
            search_text.strip(), case=False, regex=False, na=False
        )
    ]

st.caption(f"Showing {len(filtered_df)} of {len(df)} entries")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.subheader("Download Reports")
download1, download2 = st.columns(2)
with download1:
    st.download_button(
        "Download CSV Report",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="log_analysis_report.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download2:
    st.download_button(
        "Download Text Report",
        data=create_text_report(df, filename),
        file_name="log_analysis_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.caption("Automated Log File Analyzer | Python Mini Project")
