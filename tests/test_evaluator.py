import os
import json
from evaluator import evaluate_interview, generate_stub_report, combine_scores


def test_generate_stub_report_returns_structure():
    stub = generate_stub_report("short transcript")
    assert isinstance(stub, dict)
    assert "summary" in stub
    assert "questions" in stub


def test_evaluate_interview_with_stub():
    # With no GEMINI env vars set, evaluate_interview should return the stub structure
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("GEMINI_API_ENDPOINT", None)
    rpt = evaluate_interview("this is a test transcript")
    assert isinstance(rpt, dict)
    assert "summary" in rpt


def test_combine_scores():
    overall = combine_scores(8, 6, weight_technical=0.7)
    assert overall == round(0.7 * 8 + 0.3 * 6, 2)
