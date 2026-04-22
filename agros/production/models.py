from django.db import models
from plots.models import Plot
from django.utils import timezone

class Production(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='production_records')
    harvest_date = models.DateField(default=timezone.localdate)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in kg")

    def __str__(self):
        return f"Harvest from {self.plot.plot_name} on {self.harvest_date}"
