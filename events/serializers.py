from rest_framework import serializers
from .models import PortEvent

class PortEventSerializer(serializers.ModelSerializer):
    boat_mmsi = serializers.CharField(source='boat.mmsi', read_only=True)
    mmsi = serializers.CharField(source='boat.mmsi', read_only=True) # Unified field for frontend
    boat_name = serializers.CharField(source='boat.name', read_only=True)
    port_name = serializers.CharField(source='port.name', read_only=True)

    class Meta:
        model = PortEvent
        fields = ['id', 'boat', 'boat_mmsi', 'mmsi', 'boat_name', 'port', 'port_name', 'event_type', 'timestamp']
