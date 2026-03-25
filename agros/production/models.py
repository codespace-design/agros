from django.db import models
from plots.models import Plot

class Production(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='production_records')
    harvest_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantity in kg")

    def __str__(self):
        return f"Harvest from {self.plot.plot_name} on {self.harvest_date}"
