from rest_framework import viewsets
from .models import Boat
from .serializers import BoatSerializer

class BoatViewSet(viewsets.ModelViewSet):
    queryset = Boat.objects.all().order_by('-last_seen')
    serializer_class = BoatSerializer
