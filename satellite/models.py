from django.contrib.gis.db import models

class SatelliteDetection(models.Model):

    location = models.PointField()

    confidence = models.FloatField()

    image_source = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField()

    def __str__(self):
        return "Satellite detection"
