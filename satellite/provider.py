import requests
from django.conf import settings

def get_latest_satellite_image(lat, lon, zoom=15):
    """
    Récupère une image satellite haute résolution via Mapbox
    (Plus simple que Sentinel pour une démo rapide)
    """
    access_token = "TON_TOKEN_MAPBOX"
    url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},{zoom},0/800x600?access_token={access_token}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.content  # L'image en binaire
    return None