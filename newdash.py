import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Backend URL
API_URL = "https://effective-space-giggle-jjpw99q9pxwvh5wjw-8000.app.github.dev"

st.set_page_config(page_title="Strava Dashboard", layout="wide")

st.title("🏃‍♂️ Strava Activity Dashboard")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data(ttl=60)
def load_athlete():
    return requests.get(f"{API_URL}/api/athlete").json()


@st.cache_data(ttl=60)
def load_activities():
    return requests.get(f"{API_URL}/api/activities?per_page=200").json()


@st.cache_data(ttl=60)
def load_activity_details(activity_id):
    return requests.get(f"{API_URL}/api/activities/{activity_id}").json()


# -----------------------------
# Sidebar Pages
# -----------------------------
st.sidebar.title("Pages")
page = st.sidebar.selectbox("Select Page", ["Dashboard", "Activity Details"])

# -----------------------------
# Auth Check
# -----------------------------
try:
    athlete = load_athlete()
except:
    st.error("❌ Not connected to Strava. Please login first.")
    st.markdown("Open: http://localhost:8000/login")
    st.stop()


# -----------------------------
# Dashboard Page
# -----------------------------
if page == "Dashboard":
    st.subheader("👤 Athlete Profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", f"{athlete['firstname']} {athlete['lastname']}")
    with col2:
        st.metric("City", athlete.get("city", "N/A"))
    with col3:
        st.metric("Country", athlete.get("country", "N/A"))

    st.subheader("🏃 Activities")
    activities = load_activities()
    df = pd.DataFrame(activities)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["distance_km"] = df["distance"] / 1000
    df["duration_min"] = df["moving_time"] / 60
    df["pace"] = df["duration_min"] / df["distance_km"]

    # Date filters
    start = st.sidebar.date_input("Start date", df["start_date"].min().date())
    end = st.sidebar.date_input("End date", df["start_date"].max().date())
    mask = (df["start_date"].dt.date >= start) & (df["start_date"].dt.date <= end)
    df_filtered = df[mask]

    # KPIs
    st.subheader("📊 Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Activities", len(df_filtered))
    with c2:
        st.metric("Total Distance (km)", round(df_filtered["distance_km"].sum(), 1))
    with c3:
        st.metric("Total Time (hrs)", round(df_filtered["duration_min"].sum() / 60, 1))
    with c4:
        st.metric("Avg Pace (min/km)", round(df_filtered["pace"].mean(), 2))

    # Distance over time chart
    st.subheader("📈 Distance Over Time")
    fig, ax = plt.subplots()
    ax.plot(df_filtered["start_date"], df_filtered["distance_km"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")
    st.pyplot(fig)

    # Activity list
    st.subheader("📋 Activity List")
    display_cols = ["id", "name", "start_date", "type", "distance_km", "duration_min"]
    st.dataframe(df_filtered[display_cols].sort_values("start_date", ascending=False), use_container_width=True)

# -----------------------------
# Activity Details Page
# -----------------------------
elif page == "Activity Details":
    st.subheader("📍 Activity Details & Map")

    activities = load_activities()
    df = pd.DataFrame(activities)
    df["start_date"] = pd.to_datetime(df["start_date"])

    # Select activity
    activity_options = df.apply(lambda x: f"{x['name']} ({x['start_date'].date()})", axis=1)
    selected = st.selectbox("Select Activity", activity_options)

    activity_id = df.iloc[activity_options.tolist().index(selected)]["id"]
    activity = load_activity_details(activity_id)

    st.markdown(f"**Name:** {activity['name']}")
    st.markdown(f"**Type:** {activity['type']}")
    st.markdown(f"**Distance:** {round(activity['distance']/1000,2)} km")
    st.markdown(f"**Duration:** {round(activity['moving_time']/60,2)} min")
    if activity.get("average_heartrate"):
        st.markdown(f"**Avg Heart Rate:** {activity['average_heartrate']} bpm")

    # Map (if GPS data exists)
    if activity.get("map") and activity["map"].get("summary_polyline"):
        import polyline
        import numpy as np

        # Decode polyline
        coords = polyline.decode(activity["map"]["summary_polyline"])
        df_map = pd.DataFrame(coords, columns=["lat", "lon"])

        st.map(df_map)
    else:
        st.info("No GPS data available for this activity.")