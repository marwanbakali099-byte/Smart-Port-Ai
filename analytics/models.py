from django.db import models
from ports.models import Port
from django.contrib.gis.db import models


class PortMetrics(models.Model):

    port = models.ForeignKey(
        Port,
        on_delete=models.CASCADE
    )

    boats_in_port = models.IntegerField()

    entries = models.IntegerField()

    exits = models.IntegerField()

    congestion_level = models.CharField(max_length=10)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Metrics {self.port}"