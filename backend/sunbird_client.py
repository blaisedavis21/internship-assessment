import os
import time

import requests
from requests.exceptions import Timeout
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.sunbird.ai"

# connect, read — read must match how slow each upstream task can be
TIMEOUT_STT = (30, 600)
TIMEOUT_SUNFLOWER = (45, 600)
TIMEOUT_TRANSLATE = (30, 180)
TIMEOUT_TTS = (30, 300)

SUMMARY_INPUT_MAX_CHARS = 4_500
SUMMARY_RETRIES = 2
SUMMARY_RETRY_BACKOFF_SEC = 8

TTS_SPEAKER_IDS = {
    "Luganda": 248,
    "Runyankole": 243,
    "Ateso": 242,
    "Lugbara": 245,
    "Acholi": 241,
}

NLLB_TARGET_CODES = {
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Ateso": "teo",
    "Lugbara": "lgg",
    "Acholi": "ach",
}


def get_headers():
    token = os.getenv("SUNBIRD_API_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def transcribe_audio(audio_file_path):
    url = f"{BASE_URL}/tasks/stt"
    headers = {"Authorization": get_headers()["Authorization"]}
    with open(audio_file_path, "rb") as audio_file:
        files = {"audio": audio_file}
        data = {"language": "eng"}
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=TIMEOUT_STT,
        )
    if response.status_code != 200:
        raise Exception(f"STT API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("text", result.get("transcription", ""))


def summarise_text(text):
    """Sunflower simple expects form-urlencoded, not JSON."""
    url = f"{BASE_URL}/tasks/sunflower_simple"
    body = text.strip()
    if len(body) > SUMMARY_INPUT_MAX_CHARS:
        body = body[:SUMMARY_INPUT_MAX_CHARS] + "\n\n[... truncated ...]"
    instruction = (
        "Summarise the following text in a few clear sentences. "
        "Reply with only the summary, no title or preamble:\n\n"
        + body
    )
    headers = {"Authorization": get_headers()["Authorization"]}
    data = {
        "instruction": instruction,
        "model_type": "qwen",
        "temperature": "0.3",
    }
    response = None
    for attempt in range(SUMMARY_RETRIES):
        try:
            response = requests.post(
                url, headers=headers, data=data, timeout=TIMEOUT_SUNFLOWER
            )
            break
        except Timeout as e:
            if attempt + 1 >= SUMMARY_RETRIES:
                raise Exception(
                    "Summarisation timed out waiting for Sunbird AI (after "
                    f"{SUMMARY_RETRIES} tries). Try shorter text/audio, or retry later."
                ) from e
            time.sleep(SUMMARY_RETRY_BACKOFF_SEC * (attempt + 1))
    assert response is not None
    if response.status_code != 200:
        raise Exception(f"Summarisation API error {response.status_code}: {response.text}")
    result = response.json()
    if result.get("success") is False:
        raise Exception(f"Summarisation failed: {result}")
    out = result.get("response")
    if isinstance(out, str) and out.strip():
        return out.strip()
    return str(result.get("response", result))


def translate_text(text, target_language):
    url = f"{BASE_URL}/tasks/translate"
    target_code = NLLB_TARGET_CODES.get(target_language)
    if not target_code:
        raise Exception(f"Unsupported translation target: {target_language}")
    payload = {
        "source_language": "eng",
        "target_language": target_code,
        "text": text,
    }
    response = requests.post(
        url, json=payload, headers=get_headers(), timeout=TIMEOUT_TRANSLATE
    )
    if response.status_code != 200:
        raise Exception(f"Translation API error {response.status_code}: {response.text}")
    result = response.json()
    output = result.get("output")
    if isinstance(output, dict):
        err = output.get("Error") or output.get("error")
        if err:
            raise Exception(f"Translation failed: {err}")
        translated = output.get("translated_text") or output.get("text")
        if translated:
            return translated
    return result.get("translated_text") or result.get("text", str(result))


def synthesise_speech(text, language):
    url = f"{BASE_URL}/tasks/tts"
    speaker_id = TTS_SPEAKER_IDS.get(language, 248)
    payload = {"text": text, "speaker_id": speaker_id}
    response = requests.post(
        url, json=payload, headers=get_headers(), timeout=TIMEOUT_TTS
    )
    if response.status_code != 200:
        raise Exception(f"TTS API error {response.status_code}: {response.text}")
    result = response.json()
    return result.get("audio_content", result.get("audio", ""))
