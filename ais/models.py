from django.contrib.gis.db import models

class AISPosition(models.Model):

    mmsi = models.CharField(max_length=20)

    location = models.PointField()

    speed = models.FloatField(null=True, blank=True)

    heading = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField()

    def __str__(self):
        return self.mmsi
