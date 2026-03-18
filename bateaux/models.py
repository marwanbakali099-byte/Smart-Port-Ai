from django.db import models

class Boat(models.Model):
    mmsi = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    ship_type = models.IntegerField(default=30) # Important pour ETA v2
    length = models.FloatField(default=15.0)
    width = models.FloatField(default=5.0)
    tonnage = models.FloatField(default=50.0)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or 'Inconnu'} ({self.mmsi})"