---
title: Sunbird AI App
emoji: 🌻
colorFrom: yellow
colorTo: green
sdk: streamlit
sdk_version: 1.45.1
app_file: app.py
pinned: false
---

# Sunbird AI Internship Assessment

## Project Description

A Streamlit web application powered by Sunbird AI that accepts either typed text or an uploaded audio file, processes the input through transcription, summarisation, and translation into a selected Ugandan local language, and generates a spoken audio clip of the translated summary. Every intermediate result is displayed in the UI.

## Deployed Link

Live app: https://huggingface.co/spaces/BLAISE51/sunbird-ai-app

## Architecture Overview

```
Text input ──────────────────────────────────────────────┐
                                                          ▼
Audio input → Speech-to-Text → Summarise → Translate → Text-to-Speech → Output
```

- **Speech-to-Text** — Sunbird STT API ()
- **Summarisation** — Sunbird Sunflower Simple Inference (, model: qwen)
- **Translation** — Sunbird Sunflower Simple Inference (, model: qwen)
- **Text-to-Speech** — Sunbird TTS API ()

## Local Setup

1. Clone the repository.

   ```bash
   git clone https://github.com/blaisedavis21/internship-assessment.git
   cd internship-assessment
   ```

2. Create and activate a Python virtual environment.

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables.

   ```bash
   cp env_example.txt .env
   ```

   Add your Sunbird API token to  before running the app.

5. Start the app.

   ```bash
   streamlit run app.py
   ```

6. Open http://localhost:8501

## Environment Variables

| Variable            | Required | Purpose                                      |
| ------------------- | -------- | -------------------------------------------- |
|  | Yes      | Authorises requests to all Sunbird AI APIs.  |

See  for the local development template.

## Usage

1. Choose either **Text** or **Audio file** input.
2. Paste text or upload an audio file (MP3, WAV, OGG, M4A).
3. Select a target language: Luganda, Runyankole, Ateso, Lugbara, or Acholi.
4. Click **Run Pipeline**.
5. Review the transcript (audio only), summary, translated summary, and generated audio player.

## Known Limitations

- Audio files longer than 5 minutes are rejected before processing.
- Only five target languages are supported: Luganda, Runyankole, Ateso, Lugbara, and Acholi.
- The Sunbird AI free tier can be slow during peak hours — if a timeout occurs, try again with shorter input.
- Only English audio is supported for STT transcription.
- Very noisy audio can reduce transcription quality, which affects the summary, translation, and generated speech.

## Verification Notes

- Part 1 exercises are in  and covered by .
- The full pipeline is implemented in  and .
- The Streamlit frontend is in .