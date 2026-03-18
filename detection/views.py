from rest_framework import viewsets
from .models import Detection
from bateaux.models import Boat
from .serializers import DetectionSerializer
from events.services import check_entry_exit

class DetectionViewSet(viewsets.ModelViewSet):

    queryset = Detection.objects.all().order_by("-timestamp")

    serializer_class = DetectionSerializer

    def perform_create(self, serializer):
        # On laisse le serializer gérer la création du boat via le MMSI
        serializer.save()