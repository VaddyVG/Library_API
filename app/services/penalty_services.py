from datetime import datetime


def calculate_penalty(expires_at: datetime) -> float:
    days_overdue = (datetime.now() - expires_at).days
    return max(0, days_overdue * 10)
