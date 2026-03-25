from django.db import models

class Estate(models.Model):
    estate_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total area in acres")

    def __str__(self):
        return self.estate_name
