def safe_truncate(text: str, limit: int = 10000) -> str:
    if not text:
        return ""
    return text[:limit]
