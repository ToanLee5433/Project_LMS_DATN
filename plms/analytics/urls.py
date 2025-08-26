"""
Analytics URLs
"""
from django.urls import path
from .views import TeacherCourseAnalyticsAPI, StudentDashboardAPI, AdminStatsAPI

urlpatterns = [
    path('course/<int:course_id>/', TeacherCourseAnalyticsAPI.as_view(), name='teacher_analytics'),
    path('student/', StudentDashboardAPI.as_view(), name='student_dashboard'), 
    path('admin/', AdminStatsAPI.as_view(), name='admin_stats'),
]
