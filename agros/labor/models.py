from django.db import models
from django.conf import settings
from django.utils import timezone

class Labor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='worker_profile')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    class Meta:
        verbose_name_plural = "Labor"

    def __str__(self):
        return self.name

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
    ]
    
    worker = models.ForeignKey(Labor, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    
    class Meta:
        unique_together = ('worker', 'date')
        verbose_name_plural = "Attendance Records"
        
    def __str__(self):
        return f"{self.worker.name} - {self.date} ({self.status})"

class Payment(models.Model):
    worker = models.ForeignKey(Labor, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager_payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)

    def __str__(self):
        target_name = self.worker.name if self.worker else (self.manager.username if self.manager else "Unknown")
        return f"Payment of {self.amount} to {target_name} on {self.date}"
