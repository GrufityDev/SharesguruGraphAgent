import re

def sanitize_tickers(text: str) -> str:
    """
    Replace tickers like TATAMOTORS.NS / RELIANCE.BO / infy.ns
    with their plain uppercase code (TATAMOTORS, RELIANCE, INFY).
    Works for .NS, .NSE, .BSE, .BO (case-insensitive).
    """
    return re.sub(r"\b([A-Za-z0-9]+)\.(NS|NSE|BSE|BO)\b", lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)
