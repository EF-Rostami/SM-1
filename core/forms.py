# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, Teacher, ClassRoom, Attendance, Fee, ExamResult
from django.core.exceptions import ValidationError
from datetime import date


class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    admission_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )
    blood_group = forms.ChoiceField(choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ], required=False)

    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_birth','admission_date', 'current_class', 'blood_group']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean_admission_number(self):
        admission_number = self.cleaned_data.get('admission_number')
        if Student.objects.filter(admission_number=admission_number).exists():
            raise ValidationError('This admission number is already in use.')
        return admission_number

    def save(self, commit=True):
        try:
            # Create the user account
            user_data = {
                'username': self.cleaned_data['username'],
                'email': self.cleaned_data['email'],
                'first_name': self.cleaned_data['first_name'],
                'last_name': self.cleaned_data['last_name'],
                'role': User.STUDENT
            }
            user = User.objects.create_user(
                **user_data, 
                password=self.cleaned_data['password1']
            )

            # Create the student profile
            student = super().save(commit=False)
            student.user = user
            student.admission_date = self.cleaned_data['admission_date']
            
            if commit:
                student.save()
            
            return student

        except Exception as e:
            # If there's an error, delete the user if it was created
            if 'user' in locals():
                user.delete()
            raise e


class TeacherRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    date_joined = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today
    )

    class Meta:
        model = Teacher
        fields = ['employee_id', 'qualification', 'experience_years', 'subjects', 'date_joined']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if Teacher.objects.filter(employee_id=employee_id).exists():
            raise ValidationError('This employee ID is already in use.')
        return employee_id

    def save(self, commit=True):
        try:
            # Create the user account
            user_data = {
                'username': self.cleaned_data['username'],
                'email': self.cleaned_data['email'],
                'first_name': self.cleaned_data['first_name'],
                'last_name': self.cleaned_data['last_name'],
                'role': User.TEACHER
            }
            user = User.objects.create_user(
                **user_data, 
                password=self.cleaned_data['password1']
            )

            # Create the teacher profile
            teacher = super().save(commit=False)
            teacher.user = user
            teacher.date_joined = self.cleaned_data['date_joined']
            
            if commit:
                teacher.save()
                # Handle many-to-many relationship for subjects
                if 'subjects' in self.cleaned_data:
                    teacher.subjects.set(self.cleaned_data['subjects'])
            
            return teacher

        except Exception as e:
            # If there's an error, delete the user if it was created
            if 'user' in locals():
                user.delete()
            raise e


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=Attendance.ATTENDANCE_STATUS),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})
        self.fields['remarks'].widget.attrs.update({'class': 'form-control'})

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'amount', 'due_date', 'status', 'payment_method']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class_room = forms.ModelChoiceField(queryset=ClassRoom.objects.all())


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# Add this to your core/forms.py file

# In core/forms.py
class ParentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    
    # Rest of the form as previously defined
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create a new user
        user_data = {
            'username': self.cleaned_data['username'],
            'email': self.cleaned_data['email'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'phone_number': self.cleaned_data['phone_number'],
            'address': self.cleaned_data['address'],
            'role': User.PARENT
        }
        
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=self.cleaned_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number'],
            address=user_data['address'],
            role=User.PARENT
        )
        
        return user
    
class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ['student', 'marks_obtained', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

from django import forms
from .models import Event, EventRegistration

class EventRegistrationForm(forms.ModelForm):
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        help_text="Any additional information for the event organizers."
    )
    
    class Meta:
        model = EventRegistration
        fields = ['notes']  # Added notes field for participants to provide additional info

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        if not self.event or not self.student:
            raise forms.ValidationError("Missing event or student information.")
            
        # Check if student is already registered
        if EventRegistration.objects.filter(event=self.event, student=self.student).exists():
            raise forms.ValidationError("You are already registered for this event.")
        
        # Check if event has reached max participants
        if self.event.max_participants:
            current_registrations = EventRegistration.objects.filter(
                event=self.event, 
                status__in=['pending', 'confirmed']
            ).count()
            if current_registrations >= self.event.max_participants:
                raise forms.ValidationError("Sorry, this event is full.")
        
        return cleaned_data


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        # Only include fields that actually exist in your Event model
        fields = [
            'title', 
            'description', 
            'date',
            'location', 
            'image', 
            'status', 
            'max_participants'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        # Basic validation for event date
        return date