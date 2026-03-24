from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Detection, Boat
from analytics.eta_service import predict_eta_for_boat
from events.utils import handle_port_event  # ← import de la fonction port event

class DetectionSerializer(GeoFeatureModelSerializer):
    ship_type = serializers.IntegerField(write_only=True, required=False, default=30)
    
    class Meta:
        model = Detection
        geo_field = "location"
        fields = ('id', 'source', 'location', 'timestamp', 'mmsi', 'speed', 'eta_minutes', 'ship_type')
        read_only_fields = ('eta_minutes',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Inject the boat's ship_type into the GeoJSON properties for the frontend map renderer
        if instance.boat and 'properties' in ret:
            ret['properties']['ship_type'] = instance.boat.ship_type
        return ret

    def create(self, validated_data):
        mmsi = validated_data.get('mmsi')
        ship_type = validated_data.pop('ship_type', 30)
        boat = None
    
        if mmsi:
            boat, _ = Boat.objects.get_or_create(
                mmsi=mmsi,
                defaults={'ship_type': ship_type}
            )

        # 1️⃣ Créer la détection d'abord
        detection = super().create({
            **validated_data,
            'boat': boat
        })

        # 2️⃣ Calcul ETA après création
        if boat and detection.location:
            try:
                eta_val, port_id = predict_eta_for_boat(
                    boat,
                    detection.location.y,  # lat
                    detection.location.x,  # lon
                    detection.speed
                )
                detection.eta_minutes = eta_val
                detection.save()
            except Exception as e:
                print("Erreur ETA:", e)

            # 3️⃣ Gestion entrée/sortie port
            lat = detection.location.y
            lon = detection.location.x
            handle_port_event(boat, lat, lon)  # ← appel ici

        return detection