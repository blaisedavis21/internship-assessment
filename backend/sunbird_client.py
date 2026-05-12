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


def transcribe_audio(audio_file_path):
    url = f"{BASE_URL}/tasks/stt"
    headers = {"Authorization": f"Bearer {SUNBIRD_API_TOKEN}"}
    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {"language": "eng"}
        response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code != 200:
        raise Exception(f"STT API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("text", result.get("transcription", ""))


def summarise_text(text):
    url = f"{BASE_URL}/tasks/sunflower_simple"
    payload = {
        "instruction": (
            f"Please summarise the following text in a few clear sentences:\n\n{text}"
        )
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Summarisation API error {response.status_code}: {response.text}")
    result = response.json()
    output = result.get("output", {})
    if isinstance(output, dict):
        return output.get("content", "")
    return str(output)


def translate_text(text, target_language):
    url = f"{BASE_URL}/tasks/sunflower_simple"
    payload = {
        "instruction": (
            f"Translate the following text to {target_language}:\n\n{text}"
        )
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Translation API error {response.status_code}: {response.text}")
    result = response.json()
    output = result.get("output", {})
    if isinstance(output, dict):
        return output.get("content", "")
    return str(output)


def synthesise_speech(text, language):
    url = f"{BASE_URL}/tasks/tts"
    speaker_id = TTS_SPEAKER_IDS.get(language, 248)
    payload = {"text": text, "speaker_id": speaker_id}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"TTS API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("audio_content", result.get("audio", ""))
