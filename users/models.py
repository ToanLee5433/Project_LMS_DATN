from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (("admin", "Admin"), ("teacher", "Teacher"), ("student", "Student"))

    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="student")
    locale = models.CharField(max_length=5, default="vi")
    avatar = models.URLField(blank=True, null=True)
    ab_group = models.CharField(max_length=8, default="CTRL")
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
