import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.sunbird.ai"
DEFAULT_TIMEOUT = (10, 240)

TTS_LANGUAGE_CODES = {
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Ateso": "teo",
    "Lugbara": "lgg",
    "Acholi": "ach",
}


def get_auth_header():
    token = os.getenv("SUNBIRD_API_TOKEN")
    if not token:
        raise EnvironmentError("SUNBIRD_API_TOKEN is required for Sunbird API requests")
    return {"Authorization": f"Bearer {token}"}


def _post_json(endpoint, payload, timeout=DEFAULT_TIMEOUT):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(
            url,
            headers={**get_auth_header(), "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
    except requests.exceptions.Timeout as exc:
        raise Exception("Sunbird API request timed out. Try again or check your network connection.") from exc

    if response.status_code != 200:
        raise Exception(f"Sunbird API error {response.status_code}: {response.text}")
    return response.json()


def transcribe_audio(audio_file_path):
    url = f"{BASE_URL}/tasks/stt"
    with open(audio_file_path, "rb") as f:
        files = {"audio": f}
        try:
            response = requests.post(url, headers=get_auth_header(), files=files, timeout=DEFAULT_TIMEOUT)
        except requests.exceptions.Timeout as exc:
            raise Exception("Sunbird STT request timed out. Try again or use a smaller file.") from exc
    if response.status_code != 200:
        raise Exception(f"STT API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("text", result.get("transcription", ""))


def summarise_text(text):
    url = f"{BASE_URL}/tasks/sunflower_simple"
    form_data = {
        "instruction": f"Summarize the following text concisely:\n\n{text}",
        "model_type": "qwen",
        "temperature": 0.3,
    }
    try:
        response = requests.post(url, headers=get_auth_header(), data=form_data, timeout=DEFAULT_TIMEOUT)
    except requests.exceptions.Timeout as exc:
        raise Exception("Sunbird summarization request timed out. Try again or shorten the input.") from exc
    if response.status_code != 200:
        raise Exception(f"Summarisation API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("response", str(result))


def translate_text(text, target_language):
    url = f"{BASE_URL}/tasks/sunflower_simple"
    form_data = {
        "instruction": f"Translate the following text to {target_language}:\n\n{text}",
        "model_type": "qwen",
        "temperature": 0.1,
    }
    try:
        response = requests.post(url, headers=get_auth_header(), data=form_data, timeout=DEFAULT_TIMEOUT)
    except requests.exceptions.Timeout as exc:
        raise Exception("Sunbird translation request timed out. Try again or shorten the input.") from exc
    if response.status_code != 200:
        raise Exception(f"Translation API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("response", str(result))


def synthesise_speech(text, language):
    lang_code = TTS_LANGUAGE_CODES.get(language, "lug")
    payload = {"text": text, "language": lang_code, "response_mode": "url"}
    result = _post_json("/tasks/modal/tts", payload, timeout=(10, 60))
    return result.get("url", result.get("audio_url", ""))