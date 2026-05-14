import os
from backend.sunbird_client import transcribe_audio, summarise_text, translate_text, synthesise_speech

MAX_AUDIO_DURATION_SECONDS = 5 * 60


def get_audio_duration(audio_file_path):
    try:
        import wave
        if audio_file_path.endswith(".wav"):
            with wave.open(audio_file_path, "r") as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                return frames / float(rate)
    except Exception:
        pass
    return 0


def run_pipeline(text_input, audio_file_path, target_language):
    results = {
        "transcript": None,
        "summary": None,
        "translation": None,
        "audio_base64": None,
        "error": None,
    }
    try:
        if audio_file_path:
            duration = get_audio_duration(audio_file_path)
            if duration > MAX_AUDIO_DURATION_SECONDS:
                results["error"] = f"Audio is {duration/60:.1f} min. Max is 5 minutes."
                return results
            transcript = transcribe_audio(audio_file_path)
            results["transcript"] = transcript
            working_text = transcript
        elif text_input and text_input.strip():
            working_text = text_input.strip()
        else:
            results["error"] = "Please provide text input or an audio file."
            return results
        summary = summarise_text(working_text)
        results["summary"] = summary
        translation = translate_text(summary, target_language)
        results["translation"] = translation
        audio_base64 = synthesise_speech(translation, target_language)
        results["audio_base64"] = audio_base64
    except Exception as pipeline_error:
        results["error"] = str(pipeline_error)
    return results