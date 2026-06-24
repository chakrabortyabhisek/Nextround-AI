import os
import tempfile

def transcribe_file(uploaded_file):
    """Attempt to transcribe an uploaded audio file.

    Behavior:
    - If the `whisper` package is installed and `USE_WHISPER_LOCAL` env var is set, use local whisper.
    - Otherwise returns a placeholder requesting a transcript or install instructions.
    """
    use_whisper = os.getenv("USE_WHISPER_LOCAL", "false").lower() in ("1", "true", "yes")
    if use_whisper:
        try:
            import whisper
            model = whisper.load_model("small")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(uploaded_file.read())
                tmp.flush()
                result = model.transcribe(tmp.name)
                return result.get("text", "")
        except Exception as e:
            raise RuntimeError("Local Whisper transcription failed: %s" % e)

    # Fallback: ask user to paste transcript or enable local whisper
    return """
    [Transcription not performed]
    Install and enable local Whisper (set USE_WHISPER_LOCAL=1 and install `whisper`) or paste the transcript.
    """
