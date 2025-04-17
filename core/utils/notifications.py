# utils/notifications.py

# core/utils/notifications.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def send_exam_result_notification(exam_result, request=None):
    """
    Send notification to student and parent about exam results
    """
    try:
        student = exam_result.student
        parent = student.parent
        
        # Ensure parent exists and has an email
        if not parent or not parent.email:
            return False, "No parent email available"
        
        subject = f"Exam Result Notification for {student.user.get_full_name()}"
        message = (
            f"Dear Parent,\n\n"
            f"Your child {student.user.get_full_name()} has received "
            f"the following result for {exam_result.exam.name}:\n\n"
            f"Marks Obtained: {exam_result.marks_obtained} / {exam_result.exam.total_marks}\n"
            f"Remarks: {exam_result.remarks or 'No additional remarks'}\n\n"
            f"Regards,\nSchool Administration"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [parent.email],
            fail_silently=False,
        )
        
        return True, "Notification sent successfully"
    
    except Exception as e:
        # Log the error if needed
        return False, str(e)

def send_fee_reminder(fee, request=None):
    """
    Send fee reminder to student and parent
    """
    try:
        student = fee.student
        parent = student.parent
        
        # Ensure parent exists and has an email
        if not parent or not parent.email:
            return False, "No parent email available"
        
        subject = f"Fee Reminder for {student.user.get_full_name()}"
        message = (
            f"Dear Parent,\n\n"
            f"This is a reminder about the pending fee for {student.user.get_full_name()}:\n\n"
            f"Amount Due: ${fee.amount}\n"
            f"Due Date: {fee.due_date.strftime('%B %d, %Y')}\n"
            f"Status: {fee.status}\n\n"
            f"Please complete the payment before the due date to avoid any late fees.\n\n"
            f"Regards,\nSchool Administration"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [parent.email],
            fail_silently=False,
        )
        
        return True, "Fee reminder sent successfully"
    
    except Exception as e:
        # Log the error if needed
        return False, str(e)

# utils/notifications.py - simplified version
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def notify_parent_about_attendance(attendance):
    """Send notification to parent about student's attendance"""
    student = attendance.student
    if not student.parent or not student.parent.user.email:  # Updated to check parent.user.email
        return False, "Parent email not available"
    
    try:
        parent = student.parent
        student_name = student.user.get_full_name()
        date_str = attendance.date.strftime('%A, %B %d, %Y')
        
        subject = f"Attendance Update for {student_name}"
        
        if attendance.status == 'absent':
            message = f"Dear Parent,\n\nThis is to inform you that {student_name} was absent from school today ({date_str}).\n\nIf this absence was planned, please submit the appropriate leave documentation.\n\nRegards,\nSchool Administration"
        elif attendance.status == 'late':
            message = f"Dear Parent,\n\nThis is to inform you that {student_name} arrived late to school today ({date_str}).\n\nRegards,\nSchool Administration"
        else:
            return False, "Notification not needed for this status"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [parent.user.email],  # Updated to use parent.user.email
            fail_silently=False,
        )
        
        # Update attendance record
        attendance.parent_notified = True
        attendance.notification_time = timezone.now()
        attendance.save(update_fields=['parent_notified', 'notification_time'])
        
        return True, "Notification sent successfully"
        
    except Exception as e:
        return False, str(e)