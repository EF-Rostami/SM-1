# core/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Student, ClassRoom, User

class StudentModelTest(TestCase):
    def setUp(self):
        """Set up data for the whole TestCase"""
        # Create a test classroom
        self.classroom = ClassRoom.objects.create(
            name="Test Class",
            section="A",
            academic_year="2024-2025"
        )
        
        # Create a test user for student
        self.user = User.objects.create_user(
            username="teststudent",
            email="student@test.com",
            password="testpass123",
            role="student"
        )
        
        # Create a parent user
        self.parent = User.objects.create_user(
            username="testparent",
            email="parent@test.com",
            password="testpass123",
            role="parent"
        )
        
    def test_student_creation(self):
        """Test student model creation with valid data"""
        student = Student.objects.create(
            user=self.user,
            admission_number="ST12345",
            date_of_birth="2010-01-01",
            parent=self.parent,
            blood_group="O+",
            admission_date="2023-06-10",
            current_class=self.classroom
        )
        
        self.assertEqual(student.admission_number, "ST12345")
        self.assertEqual(student.user, self.user)
        self.assertEqual(student.parent, self.parent)
        self.assertEqual(student.current_class, self.classroom)