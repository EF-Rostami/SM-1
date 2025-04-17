from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'
    PARENT = 'parent'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (PARENT, 'Parent'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
    
class AcademicYear(models.Model):
    name = models.CharField(max_length=9)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other academic years to not current
            AcademicYear.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, related_name='children')
    blood_group = models.CharField(max_length=5, blank=True)
    admission_date = models.DateField()
    current_class = models.ForeignKey('ClassRoom', on_delete=models.SET_NULL, null=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, null=True)
    
    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"
    
    def get_attendance_percentage(self, start_date=None, end_date=None):
        attendance = self.attendance_set.all()
        if start_date:
            attendance = attendance.filter(date__gte=start_date)
        if end_date:
            attendance = attendance.filter(date__lte=end_date)
        
        total = attendance.count()
        if total == 0:
            return 0
        present = attendance.filter(status='present').count()
        return (present / total) * 100

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    qualification = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    date_joined = models.DateField()
    subjects = models.ManyToManyField('Subject', related_name='teachers')
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

# core/models.py (update the ClassRoom model)

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Grade 2"
    section = models.CharField(max_length=10)  # e.g., "A", "B"
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.CharField(max_length=9)  # e.g., "2024-2025"
    
    class Meta:
        unique_together = ['name', 'section', 'academic_year']
        verbose_name = "Class"
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return f"{self.name} - {self.section} ({self.academic_year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.code} - {self.name}"

from django.db import transaction
from .utils.notifications import notify_parent_about_attendance

class Attendance(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    LATE = 'late'
    EXCUSED = 'excused'
    
    ATTENDANCE_STATUS = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LATE, 'Late'),
        (EXCUSED, 'Excused'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default=ABSENT)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    time_marked = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    parent_notified = models.BooleanField(default=False)
    notification_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Prevent recursive saves when notify_parent_about_attendance updates fields
        if 'update_fields' in kwargs and kwargs['update_fields'] == ['parent_notified', 'notification_time']:
            super().save(*args, **kwargs)
            return

        is_new = self._state.adding
        old_status = None
        if not is_new:
            old_status = Attendance.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if (is_new or old_status != self.status) and \
           not self.parent_notified and \
           self.status in [self.ABSENT, self.LATE]:
            from django.db import transaction
            transaction.on_commit(lambda: notify_parent_about_attendance(self))

# models.py - add NotificationLog model
class NotificationLog(models.Model):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
    
    NOTIFICATION_TYPE = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (PUSH, 'Push Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE)
    related_to = models.CharField(max_length=50, blank=True)  # e.g., 'attendance', 'exam', etc.
    related_id = models.IntegerField(null=True, blank=True)   # e.g., attendance ID
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ])
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.user.username} - {self.subject}"


class Exam(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    total_marks = models.PositiveIntegerField()
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.subject.name}"

class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['exam', 'student']

    def has_passed(self):
        passing_marks = self.exam.total_marks * 0.4
        return self.marks_obtained >= passing_marks

    def get_status(self):
        return "Pass" if self.has_passed() else "Fail"

    def get_status_class(self):
        return "success" if self.has_passed() else "danger"

class Fee(models.Model):
    # Fee Types
    TUITION = 'tuition'
    TRANSPORT = 'transport'
    LIBRARY = 'library'
    OTHER = 'other'
    
    FEE_TYPE_CHOICES = [
        (TUITION, 'Tuition Fee'),
        (TRANSPORT, 'Transport Fee'),
        (LIBRARY, 'Library Fee'),
        (OTHER, 'Other Fee')
    ]

    # Fee Status
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    PARTIALLY_PAID = 'partially_paid'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
        (PARTIALLY_PAID, 'Partially Paid')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=50, choices=FEE_TYPE_CHOICES, default=TUITION)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=50, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, null=True)
    remarks = models.TextField(blank=True)
    




# models.py (add to existing models)
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=50, choices=[
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian')
    ], default='guardian')
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.relationship}: {self.user.get_full_name()}"
    


class TimeTable(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    period = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ['class_room', 'day_of_week', 'period']
        ordering = ['day_of_week', 'period']
    
    def __str__(self):
        return f"{self.class_room} - {self.get_day_of_week_display()} - Period {self.period}"
    
from django.db import models
from django.utils import timezone
from core.models import User, Student

class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    max_participants = models.IntegerField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="End date for multi-day events")                      
    time = models.TimeField(null=True, blank=True, help_text="Start time of the event")                
    registration_deadline = models.DateField(null=True, blank=True, help_text="Deadline for event registration")
    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ('event', 'student')
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.event.title}"