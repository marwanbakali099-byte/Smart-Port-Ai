from rest_framework import viewsets
from .models import Detection
from .serializers import DetectionSerializer


class DetectionViewSet(viewsets.ModelViewSet):

    queryset = Detection.objects.all().order_by("-timestamp")

    serializer_class = DetectionSerializer