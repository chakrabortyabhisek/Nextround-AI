import sqlite3
import json
from pathlib import Path

DB_PATH = Path.home() / ".ai_interview_coach.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        transcript TEXT,
        report_json TEXT
    )
    """
    )
    conn.commit()
    conn.close()


def save_report(transcript: str, report: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO reports (transcript, report_json) VALUES (?, ?)", (transcript, json.dumps(report)))
    conn.commit()
    conn.close()
