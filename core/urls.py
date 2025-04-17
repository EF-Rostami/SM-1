# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # ViewSets
    StudentViewSet, TeacherViewSet, ClassRoomViewSet,
    SubjectViewSet, AttendanceViewSet, ExamViewSet,
    ExamResultViewSet, FeeViewSet,
    # Views
    dashboard, StudentListView, StudentDetailView,StudentUpdateView, StudentDeleteView,
    TeacherListView, AttendanceView, 
    register_student, register_teacher
)
from .views import (
    TeacherListView, 
    TeacherDetailView, 
    TeacherUpdateView, 
    TeacherDeleteView,
    register_teacher,
    TeacherStudentListView
)
from .views import (
    ExamListView, 
    ExamCreateView, 
    ExamResultCreateView,
    ExamResultListView,
    ExamResultUpdateView,
    ExamDetailView
)

from .views import (
    UserProfileView, 
    UserProfileUpdateView, 
    change_password, activity_log
)

from .views import (
    mark_attendance,
    class_attendance_list, 
    mark_class_attendance, 
    view_class_attendance,
    attendance_view_list
)

from .views import (
    parent_children_list,
    child_detail, 
    children_attendance, 
    children_results,
    children_fees,
    register_parent,
    ParentListView, home_view, assign_student_to_parent, ParentDetailView, ParentUpdateView, ParentDeleteView, 
)

from django.urls import path
from . import views

# API Routes
router = DefaultRouter()
router.register(r'api/students', StudentViewSet)
router.register(r'api/teachers', TeacherViewSet)
router.register(r'api/classrooms', ClassRoomViewSet)
router.register(r'api/subjects', SubjectViewSet)
router.register(r'api/attendance', AttendanceViewSet)
router.register(r'api/exams', ExamViewSet)
router.register(r'api/results', ExamResultViewSet)
router.register(r'api/fees', FeeViewSet)

# Combine all URL patterns
urlpatterns = [
    # Web UI URLs
    path('dashboard/', dashboard, name='dashboard'),  
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('students/register/', register_student, name='student_register'),
    
    path('teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:pk>/edit/', TeacherUpdateView.as_view(), name='teacher_edit'),
    path('teachers/<int:pk>/delete/', TeacherDeleteView.as_view(), name='teacher_delete'),
    path('teachers/register/', register_teacher, name='teacher_register'),
    path('teacher/students/', TeacherStudentListView.as_view(), name='teacher_student_list'),

    # urls.py (add to your existing patterns)
    path('exams/', ExamListView.as_view(), name='exam_list'),
    path('exams/create/', ExamCreateView.as_view(), name='exam_create'),
    path('exams/<int:pk>/results/add/', ExamResultCreateView.as_view(), name='exam_result_create'),
    path('exams/<int:pk>/results/', ExamResultListView.as_view(), name='exam_results'),
    path('exams/<int:exam_id>/results/<int:pk>/edit/', ExamResultUpdateView.as_view(), name='exam_result_edit'),
    path('exams/<int:pk>/', ExamDetailView.as_view(), name='exam_detail'),
    
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('attendance/mark/', mark_attendance, name='mark_attendance'),
    path('attendance/classes/', class_attendance_list, name='class_attendance_list'),
    path('attendance/class/<int:class_id>/mark/', mark_class_attendance, name='mark_class_attendance'),
    path('attendance/class/<int:class_id>/view/', view_class_attendance, name='view_class_attendance'),
    path('attendance/view/', attendance_view_list, name='attendance_view_list'),

    # urls.py (add to existing patterns)
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/password/', change_password, name='change_password'),
    path('profile/activity/', activity_log, name='activity_log'),

    # urls.py
    path('parent/children/', parent_children_list, name='children_list'),
    path('parent/children/<int:student_id>/', child_detail, name='child_detail'), 
    path('parent/attendance/', children_attendance, name='children_attendance'),
    path('parent/results/', children_results, name='children_results'),
    path('parent/fees/', children_fees, name='children_fees'),
    path('parents/register/', register_parent, name='register_parent'),
    path('parents/', ParentListView.as_view(), name='parent_list'),
    path('parents/<int:parent_id>/assign-students/', assign_student_to_parent, name='assign_students_to_parent'),
    path('parents/<int:pk>/', ParentDetailView.as_view(), name='parent_detail'),
    path('parents/<int:pk>/edit/', ParentUpdateView.as_view(), name='parent_edit'),
    path('parents/<int:pk>/delete/', ParentDeleteView.as_view(), name='parent_delete'),
    
    # Include API URLs
    path('api/', include(router.urls)),
    
    # Include REST framework auth URLs
    path('api-auth/', include('rest_framework.urls')),
    path('api/classrooms/<int:class_id>/students/', views.get_students_by_class, name='get_students_by_class'),



    # Public site URLs
    path('public/', views.view_public_home, name='view_public_home'),
    path('', views.public_home, name='public_home'),
    path('about/our-school/', views.our_school, name='our_school'),
    path('about/faculty-and-staff/', views.faculty_staff, name='faculty_staff'),
    path('about/alumni/', views.alumni, name='alumni'),
    
    path('admission/request-info/', views.request_info, name='request_info'),
    path('admission/campus-visit/', views.campus_visit, name='campus_visit'),
    
    path('learning/programs/', views.programs, name='programs'),
    path('learning/after-hours/', views.after_hours, name='after_hours'),
    path('learning/athletics/', views.athletics, name='athletics'),
    
    path('news-and-events/news/', views.news, name='news'),
    path('news-and-events/events/', views.events, name='events'),
    
    path('contact/support/', views.support, name='support'),


    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Student registration views
    path('events/<int:event_id>/register/', views.event_register, name='event_register'),
    path('events/<int:event_id>/cancel/', views.event_cancel_registration, name='event_cancel_registration'),
    path('my-events/', views.my_events, name='my_events'),
    
    # Admin event management
    path('events/', views.admin_event_list, name='admin_event_list'),
    path('events/create/', views.admin_create_event, name='admin_create_event'),
    path('events/<int:event_id>/edit/', views.admin_edit_event, name='admin_edit_event'),
    path('events/<int:event_id>/delete/', views.admin_delete_event, name='admin_delete_event'),
    path('events/<int:event_id>/participants/', views.admin_event_participants, name='admin_event_participants'),

]





