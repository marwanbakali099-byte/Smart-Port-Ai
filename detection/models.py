from django.contrib.gis.db import models
from bateaux.models import Boat

class Detection(models.Model):

    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='positions', null=True)
    mmsi = models.CharField(max_length=20, null=True, blank=True)
    source = models.CharField(max_length=20, default='ais')
    location = models.PointField(spatial_index=True)
    speed = models.FloatField(default=0.0) # Feature indispensable (13.2% d'importance)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    eta_minutes = models.FloatField(null=True, blank=True)