import streamlit as st
import base64
import tempfile
import os
from dotenv import load_dotenv
from backend.pipeline import run_pipeline

load_dotenv()

st.set_page_config(page_title="Sunbird AI App", page_icon="☀️", layout="centered")
st.title("☀️ Sunbird AI — Summarise & Translate")
st.markdown("Summarise text or audio and translate it into a Ugandan local language.")
st.divider()

input_mode = st.radio("Choose input type", ["Text", "Audio file"], horizontal=True)
text_input = None
audio_file_path = None

if input_mode == "Text":
    text_input = st.text_area("Paste or type your text here", height=200, placeholder="Enter text to summarise...")
else:
    uploaded_file = st.file_uploader("Upload an audio file (MP3, WAV, OGG, M4A, max 5 minutes)", type=["mp3", "wav", "ogg", "m4a", "aac"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            audio_file_path = tmp_file.name
        st.audio(uploaded_file)

LANGUAGE_INFO = {
    "Luganda": "Widely spoken in Central Uganda",
    "Runyankole": "Spoken in the Ankole region of Western Uganda",
    "Ateso": "Spoken by the Iteso people in Eastern Uganda",
    "Lugbara": "Spoken in the West Nile region of Northwestern Uganda",
    "Acholi": "Spoken in the Acholi sub-region of Northern Uganda",
}

target_language = st.selectbox("Translate summary to", list(LANGUAGE_INFO.keys()))
st.caption(LANGUAGE_INFO[target_language])

if st.button("Run Pipeline", type="primary"):
    if not os.getenv("SUNBIRD_API_TOKEN"):
        st.error("SUNBIRD_API_TOKEN is not set. Please add it to your .env file.")
    else:
        if input_mode == "Audio file":
            with st.spinner("Transcribing audio..."):
                results = run_pipeline(text_input, audio_file_path, target_language)
        else:
            with st.spinner("Summarising and translating..."):
                results = run_pipeline(text_input, audio_file_path, target_language)
        if results["error"]:
            error_msg = results["error"]
            if "504" in error_msg or "timed out" in error_msg.lower():
                st.error("The Sunbird AI server took too long to respond. Please try again or use a shorter input.")
            elif "401" in error_msg or "403" in error_msg:
                st.error("Authentication failed. Please check your SUNBIRD_API_TOKEN.")
            elif "STT" in error_msg:
                st.error("Audio transcription failed. Make sure your audio is clear and under 5 minutes.")
            elif "Translation" in error_msg:
                st.error("Translation failed. Please try again shortly.")
            elif "TTS" in error_msg:
                st.error("Audio generation failed. Please try again shortly.")
            else:
                st.error(f"Something went wrong: {error_msg}")
        else:
            st.success("Pipeline complete!")
            st.divider()
            if results["transcript"]:
                st.subheader("Transcript")
                st.write(results["transcript"])
                st.divider()
            st.subheader("Summary")
            st.write(results["summary"])
            st.divider()
            st.subheader(f"Translation ({target_language})")
            st.write(results["translation"])
            st.divider()
            if results["audio_base64"]:
                st.subheader("Generated Audio")
                st.audio(results["audio_base64"])
            else:
                st.warning("Audio generation did not return output.")
        if audio_file_path and os.path.exists(audio_file_path):
            os.unlink(audio_file_path)