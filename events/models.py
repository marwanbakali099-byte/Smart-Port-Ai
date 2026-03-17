from django.db import models
from bateaux.models import Boat
from ports.models import Port

class PortEvent(models.Model):

    EVENT_CHOICES = [
        ('entry', 'Entry'),
        ('exit', 'Exit')
    ]

    boat = models.ForeignKey(
        Boat,
        on_delete=models.CASCADE
    )

    port = models.ForeignKey(
        Port,
        on_delete=models.CASCADE
    )

    event_type = models.CharField(
        max_length=10,
        choices=EVENT_CHOICES
    )

    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.boat} {self.event_type}"