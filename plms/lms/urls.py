from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, EnrollmentViewSet, LessonViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
urlpatterns = router.urls
