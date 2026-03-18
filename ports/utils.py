# ports/utils.py
from django.contrib.gis.geos import Point
from ports.models import Port
from django.contrib.gis.geos import Polygon
from ports.models import Port

# Tanger Ville
poly_ville = Polygon((
    (-5.85, 35.75),
    (-5.75, 35.75),
    (-5.75, 35.82),
    (-5.85, 35.82),
    (-5.85, 35.75),
))

# Tanger Med
poly_med = Polygon((
    (-5.55, 35.85),
    (-5.45, 35.85),
    (-5.45, 35.92),
    (-5.55, 35.92),
    (-5.55, 35.85),
))

# Port.objects.create(name="Tanger Ville", boundary=poly_ville)
# Port.objects.create(name="Tanger Med", boundary=poly_med)

# def is_inside_port(lat, lon):
#     inside = (
#         PORT_ZONE["lat_min"] <= lat <= PORT_ZONE["lat_max"]
#         and PORT_ZONE["lon_min"] <= lon <= PORT_ZONE["lon_max"]
#     )

#     print(f" Position: {lat}, {lon} | Inside port: {inside}")

#     return inside

def get_port_from_position(lat, lon):
    point = Point(lon, lat)

    for port in Port.objects.all():
        if port.boundary.contains(point):
            return port

    return None