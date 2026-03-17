from django.contrib.gis.db import models

class Port(models.Model):
    name = models.CharField(max_length=100)
    boundary = models.PolygonField()
    capacity = models.IntegerField()

    def __str__(self):
        return self.name