from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Detection


class DetectionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Detection
        geo_field = "location"
        fields = ('id', 'source', 'location', 'confidence', 'timestamp', 'mmsi')