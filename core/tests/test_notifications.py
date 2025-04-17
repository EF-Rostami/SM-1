# core/tests/test_notifications.py

# core/tests/test_notifications.py
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from django.test import TestCase
from django.core import mail
from django.utils import timezone
from core.models import User, Student, Attendance, ClassRoom
from core.utils.notifications import notify_parent_about_attendance
from datetime import date

class AttendanceNotificationTest(TestCase):
    def setUp(self):
        # Create parent user
        self.parent = User.objects.create_user(
            username="testparent",
            email="parent@test.com",
            password="testpass123",
            role="parent"
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username="teststudent",
            email="student@test.com",
            password="testpass123",
            role="student"
        )
        
        # Create classroom
        self.classroom = ClassRoom.objects.create(
            name="Test Class",
            section="A",
            academic_year="2024-2025"
        )
        
        # Create student profile
        self.student = Student.objects.create(
            user=self.student_user,
            admission_number="S12345",
            date_of_birth="2010-01-01",
            parent=self.parent,
            blood_group="O+",
            admission_date="2023-06-10",
            current_class=self.classroom
        )
    
    def test_absent_notification(self):
        """Test notification is sent when student is marked absent"""
        # Create attendance record
        attendance = Attendance.objects.create(
            student=self.student,
            date=date.today(),
            status='absent',
            is_present=False,
            marked_by=self.parent  # Just for testing purposes
        )
        
        # Send notification
        success, message = notify_parent_about_attendance(attendance)
        
        # Check notification was successful
        self.assertTrue(success)
        
        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn(f"Attendance Update for {self.student.user.get_full_name()}", email.subject)
        self.assertIn("was absent from school today", email.body)
        self.assertEqual(email.to, [self.parent.email])
        
        # Check attendance record was updated
        attendance.refresh_from_db()
        self.assertTrue(attendance.parent_notified)
        self.assertIsNotNone(attendance.notification_time)
    
    def test_present_no_notification(self):
        """Test no notification is sent when student is present"""
        # Create attendance record
        attendance = Attendance.objects.create(
            student=self.student,
            date=date.today(),
            status='present',
            is_present=True,
            marked_by=self.parent  # Just for testing
        )
        
        # Try to send notification
        success, message = notify_parent_about_attendance(attendance)
        
        # Should not be successful
        self.assertFalse(success)
        self.assertEqual(message, "Notification not needed for this status")
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)