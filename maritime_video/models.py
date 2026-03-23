from django.db import models

# Create your models here.
class BoatTraffic(models.Model):
    boat_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    speed = models.FloatField()
    confidence = models.FloatField()

    class Meta:
        verbose_name_plural = "Boat Traffic"