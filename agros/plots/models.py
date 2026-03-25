from django.db import models
from estates.models import Estate

class Plot(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='plots')
    plot_name = models.CharField(max_length=200)
    plant_count = models.IntegerField()

    def __str__(self):
        return f"{self.plot_name} ({self.estate.estate_name})"
