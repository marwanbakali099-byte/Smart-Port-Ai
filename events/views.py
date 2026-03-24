from rest_framework import viewsets
from .models import PortEvent
from .serializers import PortEventSerializer

class PortEventViewSet(viewsets.ModelViewSet):
    queryset = PortEvent.objects.all().order_by('-timestamp')
    serializer_class = PortEventSerializer
