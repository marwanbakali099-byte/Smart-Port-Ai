from rest_framework import viewsets
from .models import Port
from .serializers import PortSerializer

class PortViewSet(viewsets.ModelViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSerializer
