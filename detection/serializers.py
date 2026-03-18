from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Detection, Boat

class DetectionSerializer(GeoFeatureModelSerializer):
    # On garde ship_type en write_only car il sert à créer/maj le Bateau, pas la Détection
    ship_type = serializers.IntegerField(write_only=True, required=False, default=30)
    
    class Meta:
        model = Detection
        geo_field = "location"
        # On inclut 'mmsi' et 'speed' normalement (ils seront en lecture/écriture)
        fields = ('id', 'source', 'location', 'timestamp', 'mmsi', 'speed', 'ship_type')

    def create(self, validated_data):
        # On extrait les données pour le bateau
        mmsi = validated_data.get('mmsi')
        ship_type = validated_data.pop('ship_type', 30)
        speed = validated_data.get('speed', 0.0)

        boat = None
        if mmsi:
            boat, created = Boat.objects.get_or_create(
                mmsi=mmsi,
                defaults={'ship_type': ship_type}
            )
            if not created and ship_type != 30:
                boat.ship_type = ship_type
                boat.save()

        # On lie la détection au bateau trouvé/créé
        validated_data['boat'] = boat
        return super().create(validated_data)