from django.apps import AppConfig

class QuizConfig(AppConfig):
    name = 'quiz'
    default_auto_field = 'django.db.models.BigAutoField'

default_app_config = 'quiz.QuizConfig'
