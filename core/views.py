# Django REST Framework imports
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms
from django.core.validators import MaxValueValidator

# Django database imports
from django.db.models import Sum, Count, Avg, Case, When, FloatField, Q
from django.db.models.functions import Cast

# Date handling
from datetime import date

# Project imports
from core.utils.notifications import send_exam_result_notification, send_fee_reminder


from .models import (
    Student, Teacher, ClassRoom, Attendance, 
    ExamResult, Fee, Subject, Exam, User, ActivityLog, AcademicYear, TimeTable
)
from .serializers import (
    StudentSerializer, TeacherSerializer, ClassRoomSerializer,
    SubjectSerializer, AttendanceSerializer, ExamSerializer,
    ExamResultSerializer, FeeSerializer, AcademicYearSerializer
)
from .forms import StudentRegistrationForm, TeacherRegistrationForm, UserUpdateForm, ParentRegistrationForm, ExamResultForm
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.shortcuts import render, redirect
import logging

from django.shortcuts import render, redirect
from django.contrib import messages

def view_public_home(request):
    """Public home view that doesn't redirect"""
    events = Event.objects.filter(status='upcoming').order_by('date')[:3]
    
    context = {
        'events': events
    }
    return render(request, 'public/home.html', context)

def public_home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Fetch upcoming events
    events = Event.objects.filter(status='upcoming').order_by('date')[:3]
    
    context = {
        'events': events,
    }
    return render(request, 'public/home.html', context)

def home_view(request):
    """
    Home page view for the school management system
    """
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Render the home template for unauthenticated users
    return render(request, 'home.html')

# About Section Views
def our_school(request):
    context = {
        'history': 'School foundation and mission statement',
        'mission': 'Our educational philosophy',
        'vision': 'Future goals and aspirations'
    }
    return render(request, 'public/about/our_school.html', context)

def faculty_staff(request):
    context = {
        'departments': [],  # Fetch departments
        'staff_highlights': []  # Fetch notable staff members
    }
    return render(request, 'public/about/faculty_staff.html', context)

def alumni(request):
    context = {
        'notable_alumni': [],  # Fetch notable alumni
        'alumni_stories': []  # Fetch alumni success stories
    }
    return render(request, 'public/about/alumni.html', context)

# Admission Views
def request_info(request):
    if request.method == 'POST':
        # Process information request
        name = request.POST.get('name')
        email = request.POST.get('email')
        # Add logic to handle info request
        messages.success(request, 'Your request has been submitted. We will contact you soon!')
        return redirect('request_info')
    return render(request, 'public/admission/request_info.html')

def campus_visit(request):
    if request.method == 'POST':
        # Process campus visit scheduling
        name = request.POST.get('name')
        email = request.POST.get('email')
        date = request.POST.get('visit_date')
        # Add logic to handle visit scheduling
        messages.success(request, 'Your campus visit has been scheduled!')
        return redirect('campus_visit')
    return render(request, 'public/admission/campus_visit.html')

# Learning Views
def programs(request):
    context = {
        'academic_programs': [],  # Fetch academic programs
        'program_categories': []  # Categorize programs
    }
    return render(request, 'public/learning/programs.html', context)

def after_hours(request):
    context = {
        'clubs': [],  # Fetch after-school clubs
        'activities': []  # Fetch extracurricular activities
    }
    return render(request, 'public/learning/after_hours.html', context)

def athletics(request):
    context = {
        'sports_teams': [],  # Fetch sports teams
        'athletic_achievements': []  # Fetch sports achievements
    }
    return render(request, 'public/learning/athletics.html', context)

# News and Events Views
def news(request):
    context = {
        'news_items': [],  # Fetch news articles
        'featured_news': []  # Fetch featured news
    }
    return render(request, 'public/news_events/news.html', context)

def events(request):
    context = {
        'upcoming_events': [],  # Fetch upcoming events
        'past_events': []  # Fetch past events
    }
    return render(request, 'public/news_events/events.html', context)

# Contact View
def support(request):
    if request.method == 'POST':
        # Process support/contact form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Add logic to handle support request
        messages.success(request, 'Your message has been sent. We will get back to you soon!')
        return redirect('support')
    return render(request, 'public/contact/support.html')





class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        student = self.get_object()
        attendance = Attendance.objects.filter(student=student)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        student = self.get_object()
        results = ExamResult.objects.filter(student=student)
        serializer = ExamResultSerializer(results, many=True)
        return Response(serializer.data)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        teacher = self.get_object()
        subjects = teacher.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

class ClassRoomViewSet(viewsets.ModelViewSet):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        classroom = self.get_object()
        students = Student.objects.filter(current_class=classroom)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def mark_bulk(self, request):
        serializer = AttendanceSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAuthenticated]




# Regular Views
# views.py (update dashboard view)


def calculate_attendance_percentage(student):
    total_days = Attendance.objects.filter(student=student).count()
    if total_days > 0:
        present_days = Attendance.objects.filter(
            student=student, 
            status='present'  # Using status instead of is_present
        ).count()
        return round((present_days / total_days) * 100, 1)
    return 0

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    # Common data - current academic year
    current_year = date.today().year
    academic_year = f"{current_year}-{current_year+1}"
    context['academic_year'] = academic_year
    
    # Admin Dashboard
    if user.is_superuser or user.role == 'admin':
        # Basic statistics
        context['total_students'] = Student.objects.count()
        context['total_teachers'] = Teacher.objects.count()
        context['total_classes'] = ClassRoom.objects.count()
        
        # Fix Today's Attendance calculation
        today = date.today()
        total_marked = Attendance.objects.filter(date=today).count()
        if total_marked > 0:
            present_count = Attendance.objects.filter(
                date=today,
                status='present'
            ).count()
            context['attendance_percentage'] = round((present_count / total_marked) * 100, 1)
        else:
            context['attendance_percentage'] = 0

        # Fee statistics
        context['total_fees'] = Fee.objects.filter(due_date__year=today.year).aggregate(
            total=Sum('amount'),
            collected=Sum('amount', filter=Q(status='paid')),
            pending=Sum('amount', filter=Q(status='pending'))
        )

        # Recent activities
        context['recent_exams'] = Exam.objects.order_by('-date')[:5]
        context['recent_admissions'] = Student.objects.order_by('-admission_date')[:5]
        
        # Class statistics
        context['class_stats'] = ClassRoom.objects.annotate(
            student_count=Count('student', distinct=True),
            attendance_rate=Avg(
                Case(
                    When(
                        student__attendance__date=today,
                        student__attendance__status='present',
                        then=Cast(1, output_field=FloatField())
                    ),
                    default=Cast(0, output_field=FloatField())
                )
            ) * 100
        ).select_related('class_teacher')
        # Event statistics
        context['total_events'] = Event.objects.count()
        context['upcoming_events'] = Event.objects.filter(status='upcoming').count()
        context['past_events'] = Event.objects.filter(status='completed').count()

        # Recent events for admin dashboard
        context['recent_events'] = Event.objects.order_by('-date')[:5]

    # Parent Dashboard
    elif user.role == 'parent':
        try:
            # Get parent profile
            parent = Parent.objects.get(user=user)
            
            # Get all children of the parent
            children = Student.objects.filter(parent=parent).select_related(
                'user', 
                'current_class'
            )
            context['children'] = children
            
            # Initialize children attendance data
            children_attendance = []
            for child in children:
                # Get attendance records for this child
                attendance_records = Attendance.objects.filter(student=child)
                total_days = attendance_records.count()
                
                if total_days > 0:
                    present_days = attendance_records.filter(status='present').count()
                    attendance_percentage = round((present_days / total_days) * 100, 1)
                else:
                    attendance_percentage = 0
                
                children_attendance.append({
                    'student': child,
                    'attendance_percentage': attendance_percentage,
                    'recent': Attendance.objects.filter(student=child).order_by('-date')[:5]
                })
            
            context['children_attendance'] = children_attendance
            
            # Get pending fees for all children
            context['children_fees'] = Fee.objects.filter(
                student__in=children,
                status='pending'
            ).order_by('due_date').select_related('student', 'student__user')
            
            # Get recent exam results
            context['children_results'] = ExamResult.objects.filter(
                student__in=children
            ).select_related(
                'exam', 
                'student', 
                'student__user', 
                'exam__subject'
            ).order_by('-exam__date')[:10]

        except Parent.DoesNotExist:
            messages.error(request, "Parent profile not found. Please contact administrator.")
            context.update({
                'children': [],
                'children_attendance': [],
                'children_fees': [],
                'children_results': []
            })
        except Exception as e:
            messages.error(request, "Error loading parent dashboard. Please contact administrator.")
            logger = logging.getLogger(__name__)
            logger.error(f"Parent dashboard error for user {user.id}: {str(e)}")
            context.update({
                'children': [],
                'children_attendance': [],
                'children_fees': [],
                'children_results': []
            })

    # Teacher Dashboard
    elif user.role == 'teacher':
        try:
            teacher = Teacher.objects.get(user=user)
            context['teacher'] = teacher
            context['teacher_classes'] = ClassRoom.objects.filter(class_teacher=teacher)
            context['teacher_subjects'] = teacher.subjects.all()
            context['teacher_exams'] = Exam.objects.filter(
                subject__in=teacher.subjects.all()
            ).order_by('-date')[:5]
            
            # Today's attendance for teacher's class
            today = date.today()
            if ClassRoom.objects.filter(class_teacher=teacher).exists():
                class_room = ClassRoom.objects.filter(class_teacher=teacher).first()
                context['class_students'] = Student.objects.filter(current_class=class_room)
                context['today_attendance'] = Attendance.objects.filter(
                    student__current_class=class_room,
                    date=today
                )
        except Teacher.DoesNotExist:
            messages.error(request, "Teacher profile not found. Please contact administrator.")

    # Student Dashboard
    elif user.role == 'student':
        try:
            student = Student.objects.get(user=user)
            context['student'] = student
            context['student_attendance'] = Attendance.objects.filter(
                student=student
            ).order_by('-date')[:10]
            context['attendance_percentage'] = calculate_attendance_percentage(student)
            context['student_exams'] = Exam.objects.filter(
                class_room=student.current_class
            ).order_by('-date')[:5]
            context['student_fees'] = Fee.objects.filter(student=student).order_by('-due_date')[:3]
            context['student_results'] = ExamResult.objects.filter(
                student=student
            ).select_related('exam').order_by('-exam__date')[:5]
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found. Please contact administrator.")

    # Always return the render response
    return render(request, 'dashboard.html', context)

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'core/students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10
    def get_queryset(self):
        # Add ordering to prevent the pagination warning
        return Student.objects.all().order_by('user__first_name', 'admission_number')

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)



class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'core/students/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        context.update({
            'attendance': Attendance.objects.filter(student=student).order_by('-date')[:10],
            'exam_results': ExamResult.objects.filter(student=student).order_by('-exam__date'),
            'fees': Fee.objects.filter(student=student).order_by('-due_date')
        })
        return context




class StudentUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    admission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Student
        fields = ['admission_number', 'date_of_birth', 'current_class', 'blood_group', 'admission_date']
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'current_class': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        if commit:
            student.user.first_name = self.cleaned_data['first_name']
            student.user.last_name = self.cleaned_data['last_name']
            student.user.email = self.cleaned_data['email']
            student.user.save()
            student.save()
        return student

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'core/students/student_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Student information updated successfully!')
        return super().form_valid(form)



class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = 'core/students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'
    
    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student_name = student.user.get_full_name()
        
        # No need to manually delete the user
        # Django's CASCADE will handle this automatically
        messages.success(request, f'Student "{student_name}" has been deleted successfully.')
        
        return super().delete(request, *args, **kwargs)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete students.")
        return redirect('student_list')


#Attendance and Rest of views
class AttendanceView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        date_query = self.request.GET.get('date')
        class_query = self.request.GET.get('class')
        
        if date_query:
            queryset = queryset.filter(date=date_query)
        if class_query:
            queryset = queryset.filter(student__current_class_id=class_query)
            
        return queryset.order_by('-date', 'student__user__first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = ClassRoom.objects.all()
        return context

@login_required
def mark_attendance(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        class_id = request.POST.get('class_id')
        students = Student.objects.filter(current_class_id=class_id)
        
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            Attendance.objects.create(
                student=student,
                date=date,
                status=status,  # Changed from is_present=(status == 'present')
                marked_by=request.user
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance')
        
    return redirect('attendance')

def calculate_today_attendance():
    try:
        today = date.today()
        total_students = Student.objects.count()
        if total_students == 0:
            return 0
            
        present_students = Attendance.objects.filter(
            date=today,
            status='present'  # Changed from is_present=True
        ).count()
        
        return round((present_students / total_students) * 100, 1)
    except Exception:
        return 0



def is_admin(user):
    return user.is_superuser or (user.is_authenticated and user.role == 'admin')

@user_passes_test(is_admin, login_url='login')
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                student = form.save()
                messages.success(request, f'Student {student.user.get_full_name()} has been registered successfully!')
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f'Error registering student: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'core/students/student_register.html', {'form': form})

@user_passes_test(is_admin)
def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            try:
                teacher = form.save()
                messages.success(request, f'Teacher {teacher.user.get_full_name()} has been registered successfully!')
                return redirect('teacher_list')
            except Exception as e:
                messages.error(request, f'Error registering teacher: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'core/teachers/teacher_register.html', {'form': form})

def calculate_today_attendance():
    try:
        today = date.today()
        total_students = Student.objects.count()
        if total_students == 0:
            return 0
            
        present_students = Attendance.objects.filter(
            date=today,
            is_present=True
        ).count()
        
        return round((present_students / total_students) * 100, 1)
    except Exception:
        return 0
    
#Teacher Views
class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'core/teachers/teacher_list.html'  # Ensure this matches the actual path
    context_object_name = 'teachers'
    paginate_by = 10
    def get_queryset(self):
        # Add ordering to prevent the pagination warning
        return Teacher.objects.all().order_by('user__last_name')

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'core/teachers/teacher_detail.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.object
        context.update({
            'subjects': teacher.subjects.all(),
            'classes': ClassRoom.objects.filter(class_teacher=teacher)
        })
        return context

class TeacherUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Teacher
        fields = ['employee_id', 'qualification', 'experience_years', 'subjects', 'date_joined']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        teacher = super().save(commit=False)
        if commit:
            teacher.user.first_name = self.cleaned_data['first_name']
            teacher.user.last_name = self.cleaned_data['last_name']
            teacher.user.email = self.cleaned_data['email']
            teacher.user.save()
            teacher.save()
            # Handle many-to-many relationship for subjects
            self.save_m2m()
        return teacher

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherUpdateForm
    template_name = 'core/teachers/teacher_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('teacher_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Teacher information updated successfully!')
        return super().form_valid(form)

class TeacherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Teacher
    template_name = 'core/teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'
    
    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        teacher_name = teacher.user.get_full_name()
        
        # No need to manually delete the user
        # Django's CASCADE will handle this automatically
        messages.success(request, f'Teacher "{teacher_name}" has been deleted successfully.')
        
        return super().delete(request, *args, **kwargs)
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete teachers.")
        return redirect('teacher_list')
    

#Exam
class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'core/exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by subject and class if provided in GET parameters
        subject = self.request.GET.get('subject')
        class_room = self.request.GET.get('class')
        
        if subject:
            queryset = queryset.filter(subject_id=subject)
        if class_room:
            queryset = queryset.filter(class_room_id=class_room)
            
        # If user is a teacher, show only their classes' exams
        if self.request.user.role == 'teacher':
            try:
                teacher = self.request.user.teacher
                queryset = queryset.filter(class_room__class_teacher=teacher)
            except Teacher.DoesNotExist:
                queryset = Exam.objects.none()
                
        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # If user is a teacher, show only their classes
        if self.request.user.role == 'teacher':
            try:
                teacher = self.request.user.teacher
                context['classes'] = ClassRoom.objects.filter(class_teacher=teacher)
                context['subjects'] = teacher.subjects.all()
            except Teacher.DoesNotExist:
                context['classes'] = ClassRoom.objects.none()
                context['subjects'] = Subject.objects.none()
        else:
            # For admin, show all classes and subjects
            context['classes'] = ClassRoom.objects.all()
            context['subjects'] = Subject.objects.all()
            
        return context

class ExamCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Exam
    fields = ['name', 'subject', 'date', 'total_marks', 'class_room']
    template_name = 'core/exams/exam_form.html'
    success_url = reverse_lazy('exam_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ['admin', 'teacher']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role == 'teacher':
            try:
                teacher = self.request.user.teacher
                form.fields['class_room'].queryset = ClassRoom.objects.filter(class_teacher=teacher)
                form.fields['subject'].queryset = teacher.subjects.all()
            except Teacher.DoesNotExist:
                form.fields['class_room'].queryset = ClassRoom.objects.none()
                form.fields['subject'].queryset = Subject.objects.none()
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Exam created successfully!')
        return super().form_valid(form)
  
class ExamResultCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ExamResult
    form_class = ExamResultForm
    template_name = 'core/exams/exam_result_form.html'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ['admin', 'teacher']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = get_object_or_404(Exam, pk=self.kwargs['pk'])
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        # Only show students from this exam's class
        form.fields['student'].queryset = Student.objects.filter(current_class=exam.class_room)
        # Add max_value validator for marks
        form.fields['marks_obtained'].validators.append(MaxValueValidator(exam.total_marks))
        return form

    def form_valid(self, form):
        form.instance.exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        messages.success(self.request, 'Exam result added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('exam_list')
    
class ExamResultListView(LoginRequiredMixin, ListView):
    model = ExamResult
    template_name = 'core/exams/exam_results.html'
    context_object_name = 'results'
    
    def get_queryset(self):
        self.exam = get_object_or_404(Exam, pk=self.kwargs['pk'])
        return ExamResult.objects.filter(exam=self.exam).order_by('-marks_obtained')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        
        # Calculate statistics
        marks = [result.marks_obtained for result in context['results']]
        if marks:
            context['statistics'] = {
                'highest': max(marks),
                'lowest': min(marks),
                'average': sum(marks) / len(marks),
                'total_students': len(marks),
                'pass_count': sum(1 for result in context['results'] if result.has_passed()),
            }
        return context
    
class ExamResultUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ExamResult
    form_class = ExamResultForm
    template_name = 'core/exams/exam_result_form.html'
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ['admin', 'teacher']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.object.exam
        context['is_edit'] = True
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        exam = self.object.exam
        # Add max_value validator for marks
        form.fields['marks_obtained'].validators.append(MaxValueValidator(exam.total_marks))
        # Disable student field in edit mode
        form.fields['student'].widget.attrs['readonly'] = True
        form.fields['student'].disabled = True
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Exam result updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('exam_results', kwargs={'pk': self.object.exam.id})

class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'fees/fee_list.html'
    context_object_name = 'fees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        class_id = self.request.GET.get('class')
        due_date = self.request.GET.get('due_date')
        
        if status:
            queryset = queryset.filter(status=status)
        if class_id:
            queryset = queryset.filter(student__current_class_id=class_id)
        if due_date:
            queryset = queryset.filter(due_date=due_date)
            
        return queryset.order_by('due_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = ClassRoom.objects.all()
        # Add summary statistics
        context['total_pending'] = Fee.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_collected'] = Fee.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        return context

class FeeCreateForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'amount', 'due_date', 'status', 'payment_method']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Fee
    form_class = FeeCreateForm
    template_name = 'fees/fee_form.html'
    success_url = reverse_lazy('fee_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'

    def form_valid(self, form):
        messages.success(self.request, 'Fee record created successfully!')
        return super().form_valid(form)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin')
def mark_fee_paid(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    if fee.status == 'pending':
        fee.status = 'paid'
        fee.paid_date = date.today()
        fee.save()
        messages.success(request, 'Fee marked as paid successfully!')
    return redirect('fee_list')


# views.py (add to existing views)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.role == 'teacher':
            context['teacher_profile'] = Teacher.objects.get(user=self.object)
        elif self.object.role == 'student':
            context['student_profile'] = Student.objects.get(user=self.object)
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile_edit.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
    success_url = reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def activity_log(request):
    # You'll need to create an ActivityLog model to track user actions
    activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'users/activity_log.html', {'activities': activities})

#reportin view
# views.py

class StudentPerformanceReport(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'reports/student_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        
        # Get exam results
        results = ExamResult.objects.filter(student=student).select_related('exam')
        
        # Calculate subject-wise performance
        subject_performance = {}
        for result in results:
            subject = result.exam.subject
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append({
                'exam': result.exam.name,
                'marks': result.marks_obtained,
                'total': result.exam.total_marks,
                'percentage': (result.marks_obtained / result.exam.total_marks) * 100
            })
        
        # Calculate attendance statistics
        attendance = Attendance.objects.filter(student=student)
        attendance_stats = {
            'total_days': attendance.count(),
            'present_days': attendance.filter(status='present').count(),  # Changed from is_present=True
            'absent_days': attendance.filter(status='absent').count(),   # Changed from is_present=False
        }
        attendance_stats['percentage'] = (
            attendance_stats['present_days'] / attendance_stats['total_days'] * 100
            if attendance_stats['total_days'] > 0 else 0
        )
    
        
        context.update({
            'subject_performance': subject_performance,
            'attendance_stats': attendance_stats,
            'fee_status': Fee.objects.filter(student=student, status='pending'),
        })
        return context
    
    # In your views.py



    

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import ClassRoom, Student, Attendance


@login_required
@user_passes_test(lambda u: u.role in ['admin', 'teacher'])
def class_attendance_list(request):
    """View to show all classes for attendance marking"""
    classes = ClassRoom.objects.all().order_by('name', 'section')
    
    # For teachers, only show their classes
    if request.user.role == 'teacher':
        try:
            teacher = request.user.teacher
            classes = classes.filter(class_teacher=teacher)
        except:
            classes = ClassRoom.objects.none()
    
    today = date.today()
    
    # Add attendance status to each class
    for class_room in classes:
        students_count = Student.objects.filter(current_class=class_room).count()
        if students_count > 0:
            attendance_marked = Attendance.objects.filter(
                student__current_class=class_room,
                date=today
            ).count()
            
            class_room.attendance_status = {
                'total_students': students_count,
                'marked': attendance_marked,
                'percentage': int((attendance_marked / students_count) * 100) if students_count > 0 else 0,
                'is_complete': attendance_marked == students_count
            }
        else:
            class_room.attendance_status = {
                'total_students': 0,
                'marked': 0,
                'percentage': 0,
                'is_complete': False
            }
    
    context = {
        'classes': classes,
        'today': today,
    }
    return render(request, 'attendance/class_list.html', context)

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'teacher'])
def mark_class_attendance(request, class_id):
    """View to mark attendance for an entire class"""
    class_room = get_object_or_404(ClassRoom, id=class_id)
    today = date.today()
    
    # Check if user has permission for this class
    if request.user.role == 'teacher' and request.user.teacher != class_room.class_teacher:
        messages.error(request, "You don't have permission to mark attendance for this class.")
        return redirect('class_attendance_list')
    
    # Get all students in the class
    students = Student.objects.filter(current_class=class_room).order_by('user__first_name')
    
    # Print the number of students for debugging
    print(f"Number of students in class: {students.count()}")
    
    # Check if attendance already exists for today
    existing_attendance = {}
    for attendance in Attendance.objects.filter(student__in=students, date=today):
        existing_attendance[attendance.student.id] = attendance.status
    
    # Create a more template-friendly attendance status structure
    attendance_status = {}
    for student in students:
        status = existing_attendance.get(student.id, 'absent')  # Default to absent
        attendance_status[student.id] = {
            'present': status == 'present',
            'absent': status == 'absent',
            'late': status == 'late',
            'excused': status == 'excused'
        }
    
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date', today.isoformat())
        
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            # Update or create attendance record
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={
                    'status': status,
                    'remarks': remarks,
                    'marked_by': request.user,
                    'time_marked': timezone.now(),
                }
            )
        
        messages.success(request, f"Attendance for {class_room} marked successfully!")
        return redirect('class_attendance_list')
    
    context = {
        'class_room': class_room,
        'students': students,
        'today': today,
        'existing_attendance': existing_attendance,
        'attendance_status': attendance_status,
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
def view_class_attendance(request, class_id):
    """View to display attendance records for a class"""
    class_room = get_object_or_404(ClassRoom, id=class_id)
    
    # Check teacher permission
    if request.user.role == 'teacher' and request.user.teacher != class_room.class_teacher:
        messages.error(request, "You don't have permission to view attendance for this class.")
        return redirect('dashboard')
    
    students = Student.objects.filter(current_class=class_room).order_by('user__first_name')
    
    # Get date range from request or default to current month
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)
    
    attendance_records = Attendance.objects.filter(
        student__in=students,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Organize attendance records
    attendance_by_student = {}
    dates = set()
    
    for record in attendance_records:
        dates.add(record.date)
        if record.student.id not in attendance_by_student:
            attendance_by_student[record.student.id] = {
                'student': record.student,
                'attendance': {},
                'present_count': 0,
                'total_days': 0
            }
        attendance_by_student[record.student.id]['attendance'][record.date] = record
        attendance_by_student[record.student.id]['total_days'] += 1
        if record.status == 'present':
            attendance_by_student[record.student.id]['present_count'] += 1
    
    # Calculate attendance percentages
    for student_id, data in attendance_by_student.items():
        data['attendance_percentage'] = (
            round((data['present_count'] / data['total_days']) * 100, 1)
            if data['total_days'] > 0 else 0
        )
    
    context = {
        'class_room': class_room,
        'students': students,
        'attendance_by_student': attendance_by_student,
        'dates': sorted(list(dates)),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'attendance/view_class_attendance.html', context)

# Add this function directly in views.py
def notify_parent_about_attendance(attendance):
    """Send notification to parent about student's attendance"""
    student = attendance.student
    if not student.parent or not student.parent.email:
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
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [parent.email],
            fail_silently=False,
        )
        
        # Update attendance record
        from django.utils import timezone
        attendance.parent_notified = True
        attendance.notification_time = timezone.now()
        attendance.save(update_fields=['parent_notified', 'notification_time'])
        
        return True, "Notification sent successfully"
        
    except Exception as e:
        return False, str(e)
    

# Parents
@login_required
def parent_children_list(request):
    """View that shows all children of a parent user"""
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    children = Student.objects.filter(parent=request.user)
    context = {'children': children}
    return render(request, 'parent/children_list.html', context)

@login_required
def parent_child_detail(request, student_id):
    """View that shows detailed information about a specific child"""
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Ensure the student belongs to this parent
    student = get_object_or_404(Student, id=student_id, parent=request.user)
    
    context = {
        'student': student,
        'attendance': Attendance.objects.filter(student=student).order_by('-date')[:10],
        'exam_results': ExamResult.objects.filter(student=student).order_by('-exam__date'),
        'fees': Fee.objects.filter(student=student).order_by('-due_date')
    }
    return render(request, 'parent/child_detail.html', context)

# In views.py
@login_required
def child_detail(request, student_id):
    """View that shows detailed information about a specific child"""
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    try:
        # First get the parent object
        parent = Parent.objects.get(user=request.user)
        
        # Then get the student that belongs to this parent
        student = get_object_or_404(Student, id=student_id, parent=parent)
        
        context = {
            'student': student,
            'attendance': Attendance.objects.filter(student=student).order_by('-date')[:10],
            'attendance_percentage': calculate_attendance_percentage(student),
            'exam_results': ExamResult.objects.filter(student=student).order_by('-exam__date'),
            'fees': Fee.objects.filter(student=student).order_by('-due_date')
        }
        return render(request, 'core/parents/child_detail.html', context)
        
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found. Please contact administrator.")
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, "Error accessing student details. Please contact administrator.")
        return redirect('dashboard')

@user_passes_test(is_admin)
def register_parent(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                parent = form.save()
                messages.success(request, f'Parent {parent.get_full_name()} has been registered successfully!')
                return redirect('parent_list')  # You'll need to create this view too
            except Exception as e:
                messages.error(request, f'Error registering parent: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParentRegistrationForm()
    
    return render(request, 'core/parents/parent_register.html', {'form': form})
#############################################
@login_required
def children_list(request):
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
        children = Student.objects.filter(parent=parent).select_related(
            'user', 
            'current_class'
        )
        context = {'children': children}
        return render(request, 'core/parents/children_list.html', context)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('dashboard')

@login_required
def children_attendance(request):
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
        children = Student.objects.filter(parent=parent)
        children_attendance = []
        
        for child in children:
            attendance_records = Attendance.objects.filter(student=child)
            total_days = attendance_records.count()
            if total_days > 0:
                present_days = attendance_records.filter(status='present').count()
                attendance_percentage = round((present_days / total_days) * 100, 1)
            else:
                attendance_percentage = 0
                
            children_attendance.append({
                'student': child,
                'attendance_percentage': attendance_percentage,
                'recent': attendance_records.order_by('-date')[:10]
            })
        
        context = {'children_attendance': children_attendance}
        return render(request, 'core/parents/children_attendance.html', context)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('dashboard')

@login_required
def children_results(request):
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
        results = ExamResult.objects.filter(
            student__parent=parent
        ).select_related(
            'exam', 
            'student', 
            'student__user', 
            'exam__subject'
        ).order_by('-exam__date')
        
        context = {'results': results}
        return render(request, 'core/parents/children_results.html', context)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('dashboard')

@login_required
def children_fees(request):
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    try:
        parent = Parent.objects.get(user=request.user)
        fees = Fee.objects.filter(
            student__parent=parent
        ).select_related(
            'student', 
            'student__user'
        ).order_by('due_date')
        
        context = {'fees': fees}
        return render(request, 'core/parents/children_fees.html', context)
    except Parent.DoesNotExist:
        messages.error(request, "Parent profile not found.")
        return redirect('dashboard')
####################################################
@login_required
def child_detail(request, student_id):
    """View that shows detailed information about a specific child"""
    if request.user.role != 'parent':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Ensure the student belongs to this parent
    student = get_object_or_404(Student, id=student_id, parent__user=request.user)
    
    context = {
        'student': student,
        'attendance': Attendance.objects.filter(student=student).order_by('-date')[:10],
        'attendance_percentage': calculate_attendance_percentage(student),
        'exam_results': ExamResult.objects.filter(student=student).order_by('-exam__date'),
        'fees': Fee.objects.filter(student=student).order_by('-due_date')
    }
    return render(request, 'core/parents/child_detail.html', context)



from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from .models import User, Parent
# In views.py
class ParentListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/parents/parent_list.html'
    context_object_name = 'parents'
    paginate_by = 10

    def get_queryset(self):
            return User.objects.filter(role='parent').prefetch_related(
                'parent__children',
                'parent__children__current_class'
            ).order_by('first_name', 'last_name')

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for parent in context['parents']:
            try:
                parent.parent_profile = Parent.objects.get(user=parent)
            except Parent.DoesNotExist:
                parent.parent_profile = None
        return context
    

class TeacherStudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'core/students/student_list.html'
    context_object_name = 'students'
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self.request.user, 'teacher'):
            return Student.objects.none()
            
        teacher = self.request.user.teacher
        
        # Get students from classes where user is class teacher
        class_teacher_students = Student.objects.filter(
            current_class__class_teacher=teacher
        )
        
        return class_teacher_students.order_by('user__first_name', 'admission_number')
    
@login_required
@user_passes_test(lambda u: u.role in ['admin', 'teacher'])
def class_attendance_list(request):
    """View to show only classes where the user is class teacher"""
    today = date.today()
    
    if request.user.role == 'teacher':
        try:
            teacher = request.user.teacher
            classes = ClassRoom.objects.filter(class_teacher=teacher).order_by('name', 'section')
        except Teacher.DoesNotExist:
            classes = ClassRoom.objects.none()
    else:
        # Admin can see all classes
        classes = ClassRoom.objects.all().order_by('name', 'section')
    
    # Add attendance status to each class
    for class_room in classes:
        students_count = Student.objects.filter(current_class=class_room).count()
        attendance_marked = Attendance.objects.filter(
            student__current_class=class_room,
            date=today
        ).count()
        
        class_room.attendance_status = {
            'total_students': students_count,
            'marked': attendance_marked,
            'percentage': int((attendance_marked / students_count) * 100) if students_count > 0 else 0,
            'is_complete': attendance_marked == students_count
        }
    
    context = {
        'classes': classes,
        'today': today,
    }
    return render(request, 'attendance/class_list.html', context)

@login_required
def attendance_view_list(request):
    """View to show classes for attendance viewing"""
    if request.user.role == 'teacher':
        try:
            teacher = request.user.teacher
            classes = ClassRoom.objects.filter(class_teacher=teacher).order_by('name', 'section')
        except Teacher.DoesNotExist:
            classes = ClassRoom.objects.none()
    else:
        # Admin can see all classes
        classes = ClassRoom.objects.all().order_by('name', 'section')
    
    # Get attendance statistics for each class
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    for class_room in classes:
        total_students = Student.objects.filter(current_class=class_room).count()
        monthly_attendance = Attendance.objects.filter(
            student__current_class=class_room,
            date__gte=month_start,
            date__lte=today,
            status='present'
        ).count()
        
        working_days = Attendance.objects.filter(
            student__current_class=class_room,
            date__gte=month_start,
            date__lte=today
        ).values('date').distinct().count()
        
        class_room.attendance_stats = {
            'total_students': total_students,
            'monthly_attendance': monthly_attendance,
            'working_days': working_days,
            'attendance_rate': round(
                (monthly_attendance / (total_students * working_days) * 100)
                if total_students and working_days else 0,
                1
            )
        }
    
    context = {
        'classes': classes,
        'month': today.strftime('%B %Y')
    }
    return render(request, 'attendance/view_list.html', context)

# views.py

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.is_current:
            # Update current_class for all students if academic year changes
            Student.objects.filter(academic_year__is_current=True).update(
                academic_year=instance
            )

class TimeTableView(LoginRequiredMixin, ListView):
    model = TimeTable
    template_name = 'timetable/timetable_list.html'
    context_object_name = 'timetable'
    
    def get_queryset(self):
        class_id = self.request.GET.get('class')
        if class_id:
            return TimeTable.objects.filter(class_room_id=class_id).order_by('day_of_week', 'period')
        return TimeTable.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = ClassRoom.objects.all()
        class_id = self.request.GET.get('class')
        if class_id:
            context['selected_class'] = ClassRoom.objects.get(id=class_id)
            # Group timetable by day
            timetable_by_day = {}
            for day in range(7):
                timetable_by_day[day] = self.get_queryset().filter(day_of_week=day)
            context['timetable_by_day'] = timetable_by_day
        return context

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'teacher'])
def manage_timetable(request, class_id):
    class_room = get_object_or_404(ClassRoom, id=class_id)
    
    if request.method == 'POST':
        # Clear existing timetable for the class
        TimeTable.objects.filter(class_room=class_room).delete()
        
        # Process submitted timetable data
        days = range(7)
        periods = range(1, 9)  # Assuming 8 periods per day
        
        for day in days:
            for period in periods:
                subject_id = request.POST.get(f'subject_{day}_{period}')
                teacher_id = request.POST.get(f'teacher_{day}_{period}')
                start_time = request.POST.get(f'start_time_{day}_{period}')
                end_time = request.POST.get(f'end_time_{day}_{period}')
                
                if subject_id and teacher_id and start_time and end_time:
                    TimeTable.objects.create(
                        class_room=class_room,
                        day_of_week=day,
                        period=period,
                        subject_id=subject_id,
                        teacher_id=teacher_id,
                        start_time=start_time,
                        end_time=end_time
                    )
        
        messages.success(request, 'Timetable updated successfully!')
        return redirect('timetable_view')
    
    context = {
        'class_room': class_room,
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.all(),
        'existing_timetable': TimeTable.objects.filter(class_room=class_room)
    }
    return render(request, 'timetable/manage_timetable.html', context)

# Bulk Operations
@login_required
@user_passes_test(lambda u: u.role in ['admin', 'teacher'])
def bulk_mark_attendance(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        date = request.POST.get('date')
        status_data = []
        
        class_room = get_object_or_404(ClassRoom, id=class_id)
        students = Student.objects.filter(current_class=class_room)
        
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            status_data.append(
                Attendance(
                    student=student,
                    date=date,
                    status=status,
                    remarks=remarks,
                    marked_by=request.user
                )
            )
        
        # Bulk create attendance records
        Attendance.objects.bulk_create(status_data)
        messages.success(request, 'Attendance marked successfully for all students!')
        return redirect('attendance_view')
    
    context = {
        'classes': ClassRoom.objects.all(),
        'today': timezone.now().date()
    }
    return render(request, 'attendance/bulk_mark_attendance.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'admin')
def bulk_fee_create(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        fee_type = request.POST.get('fee_type')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        class_room = get_object_or_404(ClassRoom, id=class_id)
        students = Student.objects.filter(current_class=class_room)
        academic_year = AcademicYear.objects.get(is_current=True)
        
        fee_records = []
        for student in students:
            fee_records.append(
                Fee(
                    student=student,
                    fee_type=fee_type,
                    amount=amount,
                    due_date=due_date,
                    academic_year=academic_year
                )
            )
        
        # Bulk create fee records
        Fee.objects.bulk_create(fee_records)
        messages.success(request, 'Fee records created successfully for all students!')
        return redirect('fee_list')
    
    context = {
        'classes': ClassRoom.objects.all(),
    }
    return render(request, 'fees/bulk_fee_create.html', context)

class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'core/exams/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.object
        context.update({
            'results': ExamResult.objects.filter(exam=exam).select_related('student'),
            'total_students': Student.objects.filter(current_class=exam.class_room).count(),
        })
        return context
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin')
def assign_student_to_parent(request, parent_id):
    # First get the User object
    parent_user = get_object_or_404(User, id=parent_id)
    
    # Then get or create the Parent object
    parent, created = Parent.objects.get_or_create(user=parent_user)
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        try:
            # Update the students' parent field
            Student.objects.filter(id__in=student_ids).update(parent=parent)
            messages.success(request, 'Students assigned successfully!')
            return redirect('parent_list')
        except Exception as e:
            messages.error(request, f'Error assigning students: {str(e)}')
    
    # Get all unassigned students and current children
    unassigned_students = Student.objects.filter(
        Q(parent__isnull=True) | Q(parent=parent)
    ).order_by('current_class__name', 'user__first_name')
    
    current_students = Student.objects.filter(parent=parent).order_by(
        'current_class__name', 'user__first_name'
    )
    
    context = {
        'parent': parent,
        'parent_user': parent_user,
        'unassigned_students': unassigned_students,
        'current_students': current_students,
    }
    return render(request, 'core/parents/assign_students.html', context)
class ParentDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'core/parents/parent_detail.html'
    context_object_name = 'parent_user'

    def get_queryset(self):
        return User.objects.filter(role='parent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_profile'] = Parent.objects.get(user=self.object)
        context['children'] = Student.objects.filter(parent=context['parent_profile'])
        return context

class ParentUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'core/parents/parent_edit.html'
    fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
    success_url = reverse_lazy('parent_list')

    def get_queryset(self):
        return User.objects.filter(role='parent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_profile'] = Parent.objects.get(user=self.object)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Parent information updated successfully.')
        return super().form_valid(form)

class ParentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'core/parents/parent_confirm_delete.html'
    success_url = reverse_lazy('parent_list')
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'admin'

    def get_queryset(self):
        return User.objects.filter(role='parent')

    def delete(self, request, *args, **kwargs):
        parent = self.get_object()
        try:
            # Update any children to remove parent reference
            Student.objects.filter(parent__user=parent).update(parent=None)
            messages.success(request, f'Parent {parent.get_full_name()} has been deleted successfully.')
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'Error deleting parent: {str(e)}')
            return redirect('parent_list')
        
def support(request):
    return render(request, 'public/contact/support.html')

#Event related views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Event, EventRegistration, Student
from .forms import EventRegistrationForm, EventAdminForm

# Public Event Views
def event_list(request):
    """Public view of all events with filtering options"""
    events_query = Event.objects.annotate(
        registrations_count=Count('registrations')
    )
    
    # Filter options
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        events_query = events_query.filter(status=status_filter)
    else:
        # Default to upcoming events if no filter is applied
        events_query = events_query.filter(status='upcoming')
    
    # Sort options
    sort_by = request.GET.get('sort_by', 'date')
    if sort_by == 'title':
        events_query = events_query.order_by('title')
    elif sort_by == 'date':
        events_query = events_query.order_by('date')
    elif sort_by == 'registrations':
        events_query = events_query.order_by('-registrations_count')
    
    events = events_query
    
    return render(request, 'events/event_list.html', {
        'events': events,
        'current_status': status_filter or 'upcoming',
        'current_sort': sort_by,
    })

def event_detail(request, event_id):
    """Detailed view of a specific event with registration status"""
    event = get_object_or_404(Event, id=event_id)
    
    # Default values for unauthenticated users
    registered = False
    can_register = False
    registration_status = None
    
    # Check if user is logged in and is a student
    if request.user.is_authenticated:
        if request.user.role == 'student':
            try:
                student = Student.objects.get(user=request.user)
                
                # Check if already registered
                registration = EventRegistration.objects.filter(
                    event=event, 
                    student=student
                ).first()
                
                if registration:
                    registered = True
                    registration_status = registration.status
                
                # Check if can register
                can_register = not registered and event.status == 'upcoming'
                
                # Check if event is full
                if event.max_participants and can_register:
                    current_registrations = EventRegistration.objects.filter(
                        event=event, 
                        status__in=['pending', 'confirmed']
                    ).count()
                    can_register = current_registrations < event.max_participants
                
            except Student.DoesNotExist:
                can_register = False
        
        # For admin users, provide management context
        is_admin = request.user.is_superuser or request.user.role == 'admin'
    else:
        is_admin = False
    
    # Get participant count
    participants_count = EventRegistration.objects.filter(
        event=event, 
        status__in=['pending', 'confirmed']
    ).count()
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'registered': registered,
        'can_register': can_register,
        'registration_status': registration_status,
        'is_admin': is_admin,
        'participants_count': participants_count,
    })

# Student Registration Views
# Improved event_register view that properly saves the registration
@login_required
def event_register(request, event_id):
    """Register for an event with form for additional info"""
    # Ensure only students can register
    if request.user.role != 'student':
        messages.error(request, "Only students can register for events.")
        return redirect('event_list')

    try:
        student = Student.objects.get(user=request.user)
        event = get_object_or_404(Event, id=event_id)
        
        # Check if event registration is still open
        if event.status != 'upcoming':
            messages.error(request, "Registration is closed for this event.")
            return redirect('event_detail', event_id=event.id)
        
        # Check if event has a registration deadline
        if event.registration_deadline and timezone.now().date() > event.registration_deadline:
            messages.error(request, "Registration deadline has passed for this event.")
            return redirect('event_detail', event_id=event.id)
        
        # Check if already registered
        existing_registration = EventRegistration.objects.filter(
            event=event, 
            student=student
        ).first()

        if existing_registration:
            messages.warning(request, "You are already registered for this event.")
            return redirect('event_detail', event_id=event.id)
        
        # Check if event is full
        if event.max_participants:
            current_registrations = EventRegistration.objects.filter(
                event=event, 
                status__in=['pending', 'confirmed']
            ).count()
            
            if current_registrations >= event.max_participants:
                messages.error(request, "Sorry, this event is already at full capacity.")
                return redirect('event_detail', event_id=event.id)
        
        # Process the registration form if used
        if request.method == 'POST':
            # THE KEY FIX: Pass event and student to the form
            form = EventRegistrationForm(request.POST, event=event, student=student)
            if form.is_valid():
                # Create registration
                registration = form.save(commit=False)
                registration.event = event
                registration.student = student
                registration.status = 'pending'
                registration.save()
                
                messages.success(request, f"Successfully registered for {event.title}!")
                return redirect('event_detail', event_id=event.id)
        else:
            # Also pass event and student when initializing the form
            form = EventRegistrationForm(event=event, student=student)
        
        return render(request, 'events/event_register.html', {
            'event': event,
            'form': form
        })

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('event_list')

@login_required
def event_cancel_registration(request, event_id):
    """Cancel event registration with confirmation"""
    # Ensure only students can cancel registration
    if request.user.role != 'student':
        messages.error(request, "Only students can cancel event registrations.")
        return redirect('event_list')

    try:
        student = Student.objects.get(user=request.user)
        event = get_object_or_404(Event, id=event_id)
        
        # Find the registration
        registration = EventRegistration.objects.filter(
            event=event, 
            student=student
        ).first()
        
        if not registration:
            messages.warning(request, "You were not registered for this event.")
            return redirect('event_detail', event_id=event.id)
        
        # If this is a confirmation request
        if request.method == 'POST':
            registration.delete()
            messages.success(request, f"Registration for {event.title} cancelled.")
            return redirect('event_detail', event_id=event.id)
        
        # Show confirmation page
        return render(request, 'events/event_cancel_confirmation.html', {
            'event': event,
            'registration': registration
        })

    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('event_list')

@login_required
def my_events(request):
    """View for students to see all their registered events"""
    if request.user.role != 'student':
        messages.error(request, "This page is only available for students.")
        return redirect('dashboard')
    
    try:
        student = Student.objects.get(user=request.user)
        
        # Get all student registrations
        registrations = EventRegistration.objects.filter(
            student=student
        ).select_related('event').order_by('event__date')
        
        # Group by status
        upcoming_events = [r for r in registrations if r.event.status == 'upcoming']
        ongoing_events = [r for r in registrations if r.event.status == 'ongoing']
        past_events = [r for r in registrations if r.event.status == 'completed']
        
        return render(request, 'events/my_events.html', {
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'past_events': past_events,
        })
        
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard')

# Admin Event Management Views
@login_required
def admin_event_list(request):
    """List all events for admin management with advanced filtering"""
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')
    
    # Build the query with filters
    events_query = Event.objects.annotate(
        registrations_count=Count('registrations')
    )
    
    # Filter options
    status = request.GET.get('status')
    if status:
        events_query = events_query.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        events_query = events_query.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(location__icontains=search)
        )
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-date')
    events_query = events_query.order_by(sort_by)
    
    events = events_query
    
    return render(request, 'events/admin_event_list.html', {
        'events': events,
        'status_filter': status,
        'search_query': search,
        'sort_by': sort_by
    })

@login_required
def admin_create_event(request):
    """Create a new event (admin only)"""
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "You do not have permission to create events.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EventAdminForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('admin_event_list')
    else:
        form = EventAdminForm()

    return render(request, 'events/admin_event_form.html', {
        'form': form,
        'title': 'Create New Event',
        'submit_text': 'Create Event'
    })

@login_required
def admin_edit_event(request, event_id):
    """Edit an existing event (admin only)"""
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "You do not have permission to edit events.")
        return redirect('dashboard')

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventAdminForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect('admin_event_list')
    else:
        form = EventAdminForm(instance=event)

    return render(request, 'events/admin_event_form.html', {
        'form': form,
        'event': event,
        'title': f'Edit Event: {event.title}',
        'submit_text': 'Update Event'
    })

@login_required
def admin_delete_event(request, event_id):
    """Delete an event (admin only)"""
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "You do not have permission to delete events.")
        return redirect('dashboard')

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f"Event '{event_title}' deleted successfully!")
        return redirect('admin_event_list')

    return render(request, 'events/admin_event_delete_confirm.html', {
        'event': event
    })

@login_required
def admin_event_participants(request, event_id):
    """View and manage event participants (admin only)"""
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "You do not have permission to view participants.")
        return redirect('dashboard')
    
    event = get_object_or_404(Event, id=event_id)
    
    # Get all registrations for this event
    registrations = EventRegistration.objects.filter(
        event=event
    ).select_related('student', 'student__user').order_by('student__user__last_name')
    
    # Handle status updates
    if request.method == 'POST':
        action = request.POST.get('action')
        registration_ids = request.POST.getlist('registration_ids')
        
        if action and registration_ids:
            if action == 'confirm':
                EventRegistration.objects.filter(id__in=registration_ids).update(status='confirmed')
                messages.success(request, "Selected registrations have been confirmed.")
            elif action == 'reject':
                EventRegistration.objects.filter(id__in=registration_ids).update(status='rejected')
                messages.success(request, "Selected registrations have been rejected.")
            elif action == 'delete':
                EventRegistration.objects.filter(id__in=registration_ids).delete()
                messages.success(request, "Selected registrations have been deleted.")
    
    # Count by status
    pending_count = sum(1 for r in registrations if r.status == 'pending')
    confirmed_count = sum(1 for r in registrations if r.status == 'confirmed')
    rejected_count = sum(1 for r in registrations if r.status == 'rejected')
    
    return render(request, 'events/admin_event_participants.html', {
        'event': event,
        'registrations': registrations,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'rejected_count': rejected_count,
    })

# API view for problem in Attendance view-in Mark attendance section

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Student

@login_required
def get_students_by_class(request, class_id):
    """API endpoint to get students for a specific class"""
    students = Student.objects.filter(current_class_id=class_id).order_by('user__first_name')
    
    # Format student data for the frontend
    student_data = [
        {
            'id': student.id,
            'name': student.user.get_full_name() or student.user.username,
            'admission_number': getattr(student, 'admission_number', '')
        }
        for student in students
    ]
    
    return JsonResponse(student_data, safe=False)