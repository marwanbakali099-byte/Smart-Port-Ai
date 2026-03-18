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


def predict_eta_for_boat(boat, current_lat, current_lon, current_speed_kn):
    # 1. Chargement (Garder ta logique actuelle qui fonctionne pour l'objet)
    model_path = os.path.join(settings.BASE_DIR, 'ais', 'eta_tanger_model.pkl')
    # model = joblib.load(model_path)
    prediction_minutes = MODEL.predict(input_df)[0]
    if isinstance(model, dict): model = model['model']

    # 2. Calculs de base
    d_ville = haversine_scalar(current_lat, current_lon, PORTS["Tanger_Ville"][0], PORTS["Tanger_Ville"][1])
    d_med = haversine_scalar(current_lat, current_lon, PORTS["Tanger_Med"][0], PORTS["Tanger_Med"][1])
    
    distance_km = min(d_ville, d_med)
    port_encoded = 0 if d_ville < d_med else 1

    # 3. Extraction du temps (Features temporelles attendues)
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday() # 0=Lundi, 6=Dimanche

    # 4. Préparer le DataFrame avec les noms EXACTS du modèle
    # L'ORDRE DOIT ÊTRE CELUI DU MESSAGE D'ERREUR
    input_df = pd.DataFrame([{
        'distance_to_closest_port': float(distance_km),
        'hour': int(hour),
        'day_of_week': int(day_of_week),
        'port_encoded': int(port_encoded),
        'length_m': float(boat.length) if boat.length else 150.0,
        'tonnage': float(boat.tonnage) if boat.tonnage else 500.0,
        'ship_type': int(boat.ship_type) if boat.ship_type else 30,
        'current_speed': float(current_speed_kn) if current_speed_kn else 0.0
    }])

    # 5. Réorganiser les colonnes pour être sûr de l'ordre
    cols = ['distance_to_closest_port', 'hour', 'day_of_week', 'port_encoded', 
            'length_m', 'tonnage', 'ship_type', 'current_speed']
    input_df = input_df[cols]

    # 6. Prédiction
    prediction_minutes = model.predict(input_df)[0]
    
    return max(float(prediction_minutes), 1.0), port_encoded