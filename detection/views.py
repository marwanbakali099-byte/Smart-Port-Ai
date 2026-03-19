from rest_framework import viewsets
from .models import Detection
from .serializers import DetectionSerializer
# Assure-toi que ce service contient la logique de comparaison géospatiale
from events.services import check_entry_exit 

class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.all().order_by("-timestamp")
    serializer_class = DetectionSerializer

    def perform_create(self, serializer):
        # 1. On enregistre d'abord la détection en base de données
        detection = serializer.save()
        
        # 2. On déclenche la logique de vérification Entrée/Sortie
        # On passe l'objet detection qui contient le bateau (MMSI) et la location
        try:
            check_entry_exit(detection)
            print(f" Check Entry/Exit exécuté pour le MMSI: {detection.mmsi}")
        except Exception as e:
            print(f" Erreur lors du check_entry_exit: {e}")