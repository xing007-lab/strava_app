import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Backend URL
API_URL = "https://effective-space-giggle-jjpw99q9pxwvh5wjw-8000.app.github.dev"

st.set_page_config(page_title="Strava Dashboard", layout="wide")

st.title("🏃‍♂️ Strava Activity Dashboard..")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_athlete():
    try:
        response = requests.get(f"{API_URL}/api/athlete")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load athlete: {e}")
        return None


@st.cache_data(ttl=60)
def load_activities():
    try:
        response = requests.get(f"{API_URL}/api/activities?per_page=200")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load activities: {e}")
        return None


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Controls")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

# -----------------------------
# Auth Check
# -----------------------------
try:
    athlete = load_athlete()
    if athlete is None:
        st.error("❌ Not connected to Strava. Please login first.")
        st.markdown("Open: https://effective-space-giggle-jjpw99q9pxwvh5wjw-8000.app.github.dev/login")
        st.stop()
except Exception as e:
    st.error(f"❌ Error loading athlete: {e}")
    st.markdown("Open: https://effective-space-giggle-jjpw99q9pxwvh5wjw-8000.app.github.dev/login")
    st.stop()

# -----------------------------
# Profile Section
# -----------------------------
st.subheader("👤 Athlete Profile")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Name", f"{athlete['firstname']} {athlete['lastname']}")

with col2:
    st.metric("City", athlete.get("city", "N/A"))

with col3:
    st.metric("Country", athlete.get("country", "N/A"))

# -----------------------------
# Activities
# -----------------------------
st.subheader("🏃 Activities")

activities = load_activities()
if activities is None:
    st.error("Failed to load activities")
    st.stop()

df = pd.DataFrame(activities)

# Convert dates
df["start_date"] = pd.to_datetime(df["start_date"])

# Distance km
df["distance_km"] = df["distance"] / 1000

# Duration min
df["duration_min"] = df["moving_time"] / 60

# Pace min/km
df["pace"] = df["duration_min"] / df["distance_km"]

# -----------------------------
# Filters
# -----------------------------
st.sidebar.subheader("Filters")

start = st.sidebar.date_input(
    "Start date",
    df["start_date"].min().date()
)

end = st.sidebar.date_input(
    "End date",
    df["start_date"].max().date()
)

mask = (
    (df["start_date"].dt.date >= start) &
    (df["start_date"].dt.date <= end)
)

df = df[mask]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("📊 Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Activities", len(df))

with c2:
    st.metric("Total Distance (km)", round(df["distance_km"].sum(), 1))

with c3:
    st.metric("Total Time (hrs)", round(df["duration_min"].sum() / 60, 1))

with c4:
    st.metric("Avg Pace (min/km)", round(df["pace"].mean(), 2))

# -----------------------------
# Charts
# -----------------------------
st.subheader("📈 Distance Over Time")

fig, ax = plt.subplots()

ax.plot(df["start_date"], df["distance_km"])
ax.set_xlabel("Date")
ax.set_ylabel("Distance (km)")

st.pyplot(fig)

# -----------------------------
# Table
# -----------------------------
st.subheader("📋 Activity List")

display_cols = [
    "name",
    "start_date",
    "type",
    "distance_km",
    "duration_min",
    "average_heartrate"
]

st.dataframe(
    df[display_cols]
    .sort_values("start_date", ascending=False),
    use_container_width=True
)