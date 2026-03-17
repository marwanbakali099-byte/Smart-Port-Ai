from django.contrib.gis.db import models
from bateaux.models import Boat

class Detection(models.Model):

    SOURCE_CHOICES = [
        ('camera', 'Camera'),
        ('ais', 'AIS'),
        ('satellite', 'Satellite')
    ]

    boat = models.ForeignKey(
        Boat,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    mmsi = models.CharField(max_length=20, null=True, blank=True)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )

    location = models.PointField(spatial_index=True)

    confidence = models.FloatField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.source} detection"