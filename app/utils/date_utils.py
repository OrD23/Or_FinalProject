# app/utils/date_utils.py
from datetime import datetime, timedelta
from dateutil import parser

def is_recent(published_date_str: str) -> str:
    """
    Return "new" if the published date is within the last 30 days,
    otherwise "not new".
    """
    try:
        published_date = parser.parse(published_date_str)
        if datetime.utcnow() - published_date <= timedelta(days=30):
            return "new"
        else:
            return "not new"
    except Exception:
        return "not new"
