import os
import json
import requests
from typing import Dict, Any


GEMINI_ENDPOINT = os.getenv("GEMINI_API_ENDPOINT")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_TYPE = os.getenv("GEMINI_API_TYPE", "generic").lower()  # 'google', 'openai', or 'generic'


def combine_scores(tech: float, comm: float, weight_technical: float = 0.7) -> float:
    """Combine technical and communication scores into an overall score.

    Default gives more weight to technical ability but can be tuned.
    """
    try:
        tech_v = float(tech)
        comm_v = float(comm)
    except Exception:
        return None
    return round(weight_technical * tech_v + (1 - weight_technical) * comm_v, 2)


def call_gemini(prompt: str) -> Dict[str, Any]:
    """Call Gemini-like API endpoint with a simple POST. Expects JSON response.

    If no GEMINI_KEY is set, returns a stubbed response for local testing.
    """
    if not GEMINI_KEY or not GEMINI_ENDPOINT:
        # Return a lightweight stub to allow local testing without credentials
        return {
            "summary": "Stub summary: enable GEMINI_API_KEY and GEMINI_API_ENDPOINT for real responses.",
            "questions": [],
            "weak_topics": ["Data structures", "Behavioral questions"],
            "study_plan": [
                "Review arrays and hash maps",
                "Practice system design fundamentals",
            ],
            "follow_ups": ["How would you scale X?", "Explain the time complexity of your solution."],
        }

    headers = {"Authorization": f"Bearer {GEMINI_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_tokens": 1200}
    resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


import os
import json
import requests
import re
from typing import Dict, Any


GEMINI_ENDPOINT = os.getenv("GEMINI_API_ENDPOINT")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


def call_gemini(prompt: str) -> Any:
    """Call Gemini-like API endpoint.

    If no credentials are configured, return a structured stub suitable for the UI.
    """
    if not GEMINI_KEY or not GEMINI_ENDPOINT:
        return generate_stub_report(prompt)

    # Support different provider types; default generic POST
    if GEMINI_API_TYPE == "google":
        return call_gemini_google(prompt)
    if GEMINI_API_TYPE == "openai":
        return call_gemini_openai(prompt)

    headers = {"Authorization": f"Bearer {GEMINI_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_tokens": 1600}
    resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.text


def call_gemini_google(prompt: str) -> str:
    """Call Google Generative API-style endpoint. This is a minimal adapter.

    Expects `GEMINI_API_ENDPOINT` to be something like
    `https://generativelanguage.googleapis.com/v1beta2/models/{model}:generate`.
    """
    headers = {"Authorization": f"Bearer {GEMINI_KEY}", "Content-Type": "application/json"}
    # For safety, use a simple request body compatible with the GA API
    body = {"prompt": {"text": prompt}, "maxOutputTokens": 800}
    resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    try:
        data = resp.json()
        # Attempt to extract text from common response shapes
        if isinstance(data, dict):
            # Google returns `candidates` or `output` fields in some versions
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0].get("content", json.dumps(data))
            if "output" in data and isinstance(data["output"], list):
                return "\n".join([o.get("content", "") for o in data["output"]])
        return resp.text
    except Exception:
        return resp.text


def call_gemini_openai(prompt: str) -> str:
    """Call an OpenAI-compatible text generation endpoint.

    This expects `GEMINI_API_ENDPOINT` to be an OpenAI-style completions/chat endpoint.
    """
    headers = {"Authorization": f"Bearer {GEMINI_KEY}", "Content-Type": "application/json"}
    body = {"model": "gpt-4o-mini", "prompt": prompt, "max_tokens": 1200}
    resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    try:
        d = resp.json()
        # Try common shapes
        if "choices" in d and d["choices"]:
            return d["choices"][0].get("text", resp.text)
        return resp.text
    except Exception:
        return resp.text


def build_prompt(transcript: str) -> str:
    schema = {
        "summary": "string",
        "questions": [
            {
                "question": "string",
                "answer_excerpt": "string",
                "score_technical": "0-10 number",
                "score_communication": "0-10 number",
                "score_overall": "0-10 number",
                "feedback": "string",
                "topics": ["list of short topic strings"]
            }
        ],
        "weak_topics": ["list of topic strings"],
        "study_plan": ["list of actionable steps, day-by-day suggested"],
        "follow_ups": ["likely follow-up question strings"]
    }

    instructions = (
        "You are an interview debrief assistant. Given the full transcript of a technical interview,"
        " extract the questions asked and the candidate's answers. For each Q/A pair, score technical correctness and"
        " communication separately (0-10), provide an overall score (0-10), give concise feedback, and list related topics."
        " Identify the candidate's weak topics, produce a 7-day personalized study plan (list of steps), and generate likely follow-up questions."
        " IMPORTANT: Return ONLY a single JSON object that exactly follows this schema: "
        f"{json.dumps(schema)}\n\n"
    )
    # Truncate transcript to avoid huge prompts
    transcript_excerpt = transcript[:18000]
    return f"{instructions}\nTranscript:\n{transcript_excerpt}"


def parse_model_output(raw: Any) -> Dict[str, Any]:
    """Try to parse model output into the expected dict structure."""
    if isinstance(raw, dict):
        return raw

    text = str(raw)
    # Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        # Attempt to extract JSON substring
        m = re.search(r"\{\s*\"summary\".*\}\s*$", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

    # As a last resort, wrap a minimal response
    return {
        "summary": text[:2000],
        "questions": [],
        "weak_topics": [],
        "study_plan": [],
        "follow_ups": [],
    }


def generate_stub_report(prompt_or_transcript: str) -> Dict[str, Any]:
    """Create a realistic stubbed JSON response for local testing.

    This uses simple heuristics to produce example questions and plan entries.
    """
    transcript = prompt_or_transcript
    excerpt = transcript[:400]
    return {
        "summary": f"Local stub: short summary based on transcript excerpt: {excerpt}",
        "questions": [
            {
                "question": "Describe a time you optimized a slow algorithm.",
                "answer_excerpt": "I profiled the code and replaced nested loops with a hashmap-based approach...",
                "score_technical": 6,
                "score_communication": 7,
                "score_overall": 6.5,
                "feedback": "Good debugging approach; provide clearer complexity analysis next time.",
                "topics": ["algorithms", "profiling", "time-complexity"]
            },
            {
                "question": "How would you scale a web service to handle more traffic?",
                "answer_excerpt": "Use load balancers, caching, and database sharding...",
                "score_technical": 7,
                "score_communication": 6,
                "score_overall": 6.5,
                "feedback": "Solid ideas; include metrics and tradeoffs for each option.",
                "topics": ["scalability", "caching", "databases"]
            },
        ],
        "weak_topics": ["time-complexity analysis", "system design metrics"],
        "study_plan": [
            "Day 1: Review Big-O notation and common data structures",
            "Day 2: Practice algorithm problems on arrays and hash maps (2 problems)",
            "Day 3: Read about load balancing and caching strategies",
            "Day 4: Implement a small caching layer in a sample app",
            "Day 5: Study database sharding and partitioning patterns",
            "Day 6: Mock interview: answer 3 system design questions",
            "Day 7: Review incorrect answers and write concise explanations",
        ],
        "follow_ups": [
            "What is the time complexity of your optimized solution?",
            "How would you measure the impact of your caching strategy?",
        ],
    }


def evaluate_interview(transcript: str) -> Dict[str, Any]:
    prompt = build_prompt(transcript)
    raw = call_gemini(prompt)
    parsed = parse_model_output(raw)
    return parsed
