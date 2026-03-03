import requests

BASE_URL = "https://www.strava.com/api/v3"


class StravaClient:

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_athlete(self):
        return requests.get(
            f"{BASE_URL}/athlete",
            headers=self._headers()
        ).json()

    def get_activities(self, page=1, per_page=30):
        return requests.get(
            f"{BASE_URL}/athlete/activities",
            headers=self._headers(),
            params={"page": page, "per_page": per_page}
        ).json()

    def get_activity(self, activity_id: int):
        return requests.get(
            f"{BASE_URL}/activities/{activity_id}",
            headers=self._headers()
        ).json()