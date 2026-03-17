from django.db import models

class Boat(models.Model):

    SIZE_CHOICES = [
        ('small', 'Small Boat'),
        ('medium', 'Medium Boat'),
        ('large', 'Large Boat')
    ]

    mmsi = models.CharField(max_length=20, null=True, blank=True)

    size_class = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES
    )

    first_seen = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Boat {self.id}"