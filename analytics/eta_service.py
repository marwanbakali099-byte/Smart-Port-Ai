import joblib
import pandas as pd
import os
from django.conf import settings
# On importe la fonction haversine depuis ton fichier de modèle
from ais.ETA_model_v2 import haversine_scalar 
from datetime import datetime
from .model_loader import MODEL

# Coordonnées des ports (Lat, Lon)
PORTS = {
    "Tanger_Ville": (35.788, -5.808),
    "Tanger_Med": (35.890, -5.500)
}

from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def predict_eta_for_boat(boat, current_lat, current_lon, current_speed_kn):

    # 🔹 sécurité
    if not boat or current_lat is None or current_lon is None:
        return None, None

    # 🔹 vitesse safe
    speed = current_speed_kn if current_speed_kn and current_speed_kn > 0 else 1.0

    # 🔹 ports (Tanger Ville / Med)
    d_ville = haversine_scalar(current_lat, current_lon, PORTS["Tanger_Ville"][0], PORTS["Tanger_Ville"][1])
    d_med = haversine_scalar(current_lat, current_lon, PORTS["Tanger_Med"][0], PORTS["Tanger_Med"][1])
    
    distance_km = min(d_ville, d_med)
    port_encoded = 0 if d_ville < d_med else 1

    # 🔹 temps
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()

    # ✅ CRÉER input_df AVANT PREDICT
    input_df = pd.DataFrame([{
        'distance_to_closest_port': float(distance_km),
        'hour': int(hour),
        'day_of_week': int(day_of_week),
        'port_encoded': int(port_encoded),
        'length_m': float(boat.length) if boat.length else 150.0,
        'tonnage': float(boat.tonnage) if boat.tonnage else 500.0,
        'ship_type': int(boat.ship_type) if boat.ship_type else 30,
        'current_speed': float(speed)
    }])

    cols = [
        'distance_to_closest_port', 'hour', 'day_of_week',
        'port_encoded', 'length_m', 'tonnage',
        'ship_type', 'current_speed'
    ]

    input_df = input_df[cols]

    # ✅ UTILISER MODEL (pas model)
    prediction_minutes = MODEL.predict(input_df)[0]

    return max(float(prediction_minutes), 1.0), port_encoded