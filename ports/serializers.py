from rest_framework import serializers
from .models import Port

class PortSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    lon = serializers.SerializerMethodField()
    congestion = serializers.SerializerMethodField()
    boats_in_port = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ['id', 'name', 'lat', 'lon', 'congestion', 'boats_in_port', 'capacity']

    def get_lat(self, obj):
        # Return centroid latitude of the polygon boundary
        return obj.boundary.centroid.y if obj.boundary else 0.0

    def get_lon(self, obj):
        # Return centroid longitude
        return obj.boundary.centroid.x if obj.boundary else 0.0

    def get_congestion(self, obj):
        return 'LOW' # We can default to LOW or compute later

    def get_boats_in_port(self, obj):
        return 0 # Default to 0, to be properly computed later
