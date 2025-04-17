# utils/tasks.py

from datetime import date, timedelta
from core.models import Fee
from .notifications import send_fee_reminder

def send_fee_reminders():
    """
    Task to send fee reminders for fees due in the next 7 days
    """
    upcoming_due_date = date.today() + timedelta(days=7)
    pending_fees = Fee.objects.filter(
        status='pending',
        due_date=upcoming_due_date
    )
    
    for fee in pending_fees:
        send_fee_reminder(fee, None)