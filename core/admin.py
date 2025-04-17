# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Student, Teacher, ClassRoom, 
    Subject, Attendance, Exam, ExamResult, Fee, AcademicYear
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Contact info', {'fields': ('phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),  # Make sure this is a tuple with a comma
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email', 'first_name', 'last_name'),
        }),
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'get_full_name', 'current_class', 'date_of_birth', 'admission_date')
    list_filter = ('current_class', 'admission_date')
    search_fields = ('admission_number', 'user__first_name', 'user__last_name')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'qualification', 'experience_years', 'date_joined')
    list_filter = ('date_joined', 'qualification')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name')
    filter_horizontal = ('subjects',)
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'class_teacher', 'academic_year')
    list_filter = ('academic_year', 'name')
    search_fields = ('name', 'section', 'class_teacher__user__first_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'credits')
    search_fields = ('name', 'code')

# admin.py
from django.contrib import admin
from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by', 'time_marked']  # Removed 'is_present'
    list_filter = ['date', 'status']  # Removed 'is_present'
    search_fields = ['student__user__first_name', 'student__user__last_name', 'student__admission_number']
    date_hierarchy = 'date'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('time_marked',)
        return ()

admin.site.register(Attendance, AttendanceAdmin)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'date', 'total_marks', 'class_room')
    list_filter = ('date', 'class_room', 'subject')
    search_fields = ('name', 'subject__name')
    date_hierarchy = 'date'

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'marks_obtained')
    list_filter = ('exam__date', 'exam__subject')
    search_fields = ('student__user__first_name', 'exam__name')

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'due_date', 'status', 'paid_date')
    list_filter = ('status', 'due_date', 'paid_date')
    search_fields = ('student__user__first_name', 'student__admission_number')
    date_hierarchy = 'due_date'

# admin.py (add this to your imports)
from .models import (
    User, Student, Teacher, ClassRoom, 
    Subject, Attendance, Exam, ExamResult, Fee, Parent
)

# admin.py (add this registration)
@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'relationship', 'occupation')
    list_filter = ('relationship',)
    search_fields = ('user__first_name', 'user__last_name', 'occupation')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Full Name'

@admin.register(AcademicYear)
class AcademicYear(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('name',)
    search_fields = ('name', 'start_date', 'end_date')