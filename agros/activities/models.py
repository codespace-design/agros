from django.db import models
from plots.models import Plot
from labor.models import Labor
from django.utils import timezone

class ActivityCategory(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Activity Categories"

    def __str__(self):
        return self.category_name

class Activity(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='activities')
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    activity_date = models.DateField(default=timezone.localdate)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.category.category_name} - {self.plot.plot_name} ({self.activity_date})"

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    worker = models.ForeignKey(Labor, on_delete=models.CASCADE, related_name='assignments')
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    task_date = models.DateField(default=timezone.localdate)
    wage = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task for {self.worker.name} on {self.task_date}"
