from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    WORKER = 'WORKER'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Estate Manager'),
        (WORKER, 'Labor'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=WORKER)
    status = models.BooleanField(default=True)  # Active/Inactive

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class SystemSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name_plural = "System Settings"
