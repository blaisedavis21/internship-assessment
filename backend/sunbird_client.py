import os
import requests

SUNBIRD_API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")
BASE_URL = "https://api.sunbird.ai"

HEADERS = {
    "Authorization": f"Bearer {SUNBIRD_API_TOKEN}",
    "Content-Type": "application/json",
}

TTS_SPEAKER_IDS = {
    "Luganda": 248,
    "Runyankole": 243,
    "Ateso": 242,
    "Lugbara": 245,
    "Acholi": 241,
}
