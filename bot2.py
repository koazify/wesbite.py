import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="Animal Company Tracker", layout="wide")
st.title("Animal Company Update Tracker")

STATUS_FILE = "status.json"
CURRENT_VERSION_FILE = "current-update.txt"
HISTORY_FILE = "update-history.json"

def load_status():
    if os.path.isfile(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def load_current_version():
    if os.path.isfile(CURRENT_VERSION_FILE):
        with open(CURRENT_VERSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Unknown"

def load_update_history():
    if os.path.isfile(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

status = load_status()
is_online = status.get("lastOnline", False)

current_version = load_current_version()

st.subheader(f"📌 Current Version: `{current_version}`")

with st.expander("📜 Update History"):
    update_history = load_update_history()
    if not update_history:
        st.info("No update history found.")
    else:
        for update in reversed(update_history):
            st.markdown(f"### 🔸 Version: `{update['version']}`")
            st.markdown(f"**Date:** `{update['date']}`")
            st.markdown("---")

st.sidebar.title("🤖 Discord Bot Status")
if is_online:
    st.sidebar.success(f"✅ Bot is Online")
else:
    st.sidebar.error("❌ Bot is Offline")

st.sidebar.write("Connected channel: `#updates`")
st.sidebar.write("Auto-checks every minute")

st.markdown("### ℹ️ This site is powered by ACUT and auto-updates automatically")
st.caption("Animal Company Update Tracker © 2025")
