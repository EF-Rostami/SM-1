# In core/tests/test_forms.py
from django.test import TestCase
from core.forms import StudentRegistrationForm
from core.models import ClassRoom, User  # Import the models you need

class StudentFormTest(TestCase):
    def setUp(self):
        # Create a classroom first so we can reference it
        self.classroom = ClassRoom.objects.create(
            name="Test Class",
            section="A",
            academic_year="2024-2025"
        )

    def test_student_registration_form(self):
        """Test the student registration form validation"""
        # Test with invalid data
        form_data = {
            'username': 'newstudent',
            # Missing required fields
        }
        form = StudentRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test with valid data - now use the ID of the classroom we created
        form_data = {
            'username': 'newstudent',
            'password1': 'Secure123!',
            'password2': 'Secure123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'admission_number': 'S12345',
            'date_of_birth': '2010-05-15',
            'admission_date': '2023-09-01',
            'current_class': self.classroom.id,  # Use the actual classroom ID
            'blood_group': 'B+',
            # Add all other required fields
        }
        form = StudentRegistrationForm(data=form_data)
        # Print form errors for debugging if needed
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())