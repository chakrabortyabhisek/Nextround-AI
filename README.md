# AI Interview Debrief & Improvement Coach ⭐

A Streamlit app that helps candidates learn from completed interviews by extracting questions, evaluating answers, identifying weak topics, and generating a personalized study plan.

Features
- Upload interview audio (MP3/WAV) or paste transcript
- Extract questions and evaluate each answer
- Score communication and technical accuracy
- Identify weak topics and generate a study plan
- Generate likely follow-up interview questions
- Save reports to a local SQLite DB

Tech Stack
- Python
- Streamlit
- Gemini API (configurable)
- Whisper (optional local speech-to-text)
- SQLite for persistence

Quickstart

1. Create a venv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. (Optional) Enable local Whisper transcription:

```bash
# Install ffmpeg and set env var
pip install -U whisper pydub
setx USE_WHISPER_LOCAL 1
```

3. (Optional) Configure Gemini / Generative model API (if you have credentials):

The evaluator supports multiple provider styles via `GEMINI_API_TYPE`.

`GEMINI_API_TYPE` values:
- `google` — Google Generative API endpoint (expects JSON body with `prompt.text`)
- `openai` — OpenAI-compatible endpoint (completions/chat)
- `generic` — Generic POST to `GEMINI_API_ENDPOINT` with `{prompt, max_tokens}` body

Example (Windows PowerShell):

```powershell
setx GEMINI_API_ENDPOINT "https://your.gemini.endpoint/your_path"
setx GEMINI_API_KEY "your_api_key"
setx GEMINI_API_TYPE "google"
```

4. Run the app:

```bash
streamlit run app.py
```

Notes
- The project includes a stubbed Gemini response when no API key/endpoint are provided so you can try the UI locally.
- Run unit tests:

```bash
pytest -q
```
- For production use, replace the `call_gemini` implementation in `evaluator.py` with the official Gemini client code and robust parsing of model outputs.

Want help wiring your Gemini account or improving scoring prompts? Ask me and I can implement the integration.