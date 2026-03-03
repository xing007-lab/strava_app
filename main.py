from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import time

from auth import get_auth_url, exchange_code_for_token, refresh_access_token
from strava import StravaClient

app = FastAPI()

# TEMP storage (use DB in production)
TOKENS = {}


@app.get("/")
def home():
    return {
        "message": "Strava API Service",
        "login": "/login"
    }


@app.get("/login")
def login():
    return RedirectResponse(get_auth_url())


@app.get("/callback")
def callback(code: str):

    data = exchange_code_for_token(code)

    if "access_token" not in data:
        raise HTTPException(400, "Auth failed")

    TOKENS["access"] = data["access_token"]
    TOKENS["refresh"] = data["refresh_token"]
    TOKENS["expires_at"] = data["expires_at"]

    return {"status": "connected"}


def get_client():
    if not TOKENS:
        raise HTTPException(401, "Not authenticated")

    # Refresh if expired
    if time.time() > TOKENS["expires_at"]:
        data = refresh_access_token(TOKENS["refresh"])

        TOKENS.update({
            "access": data["access_token"],
            "refresh": data["refresh_token"],
            "expires_at": data["expires_at"]
        })

    return StravaClient(TOKENS["access"])


@app.get("/api/athlete")
def athlete():
    client = get_client()
    return client.get_athlete()


@app.get("/api/activities")
def activities(page: int = 1, per_page: int = 30):
    client = get_client()
    return client.get_activities(page, per_page)


@app.get("/api/activities/{activity_id}")
def activity(activity_id: int):
    client = get_client()
    return client.get_activity(activity_id)