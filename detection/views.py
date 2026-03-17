from rest_framework import viewsets
from .models import Detection
from bateaux.models import Boat
from .serializers import DetectionSerializer
from events.services import check_entry_exit

class DetectionViewSet(viewsets.ModelViewSet):

    queryset = Detection.objects.all().order_by("-timestamp")

    serializer_class = DetectionSerializer

    def perform_create(self, serializer):
        # Crée automatiquement le bateau si MMSI fourni
        mmsi = self.request.data.get("mmsi")
        boat = None
        if mmsi:
            boat, _ = Boat.objects.get_or_create(mmsi=mmsi)

        # Sauvegarde la détection
        detection = serializer.save(boat=boat)

        # Vérifie entry / exit
        if boat:
            check_entry_exit(boat, detection)
