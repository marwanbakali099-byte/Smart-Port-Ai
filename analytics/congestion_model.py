import xgboost as xgb
import pandas as pd
import os
import numpy as np
from django.conf import settings

class CongestionPredictor:
    def __init__(self):
        # On définit le chemin vers le fichier JSON du modèle dans le dossier analytics
        self.model_path = os.path.join(settings.BASE_DIR, 'analytics', 'xgboost_congestion_model.json')
        self.model = xgb.Booster()
        self.model.load_model(self.model_path)

    def predict(self, hours, fishing_hours, mmsi_present):
        # 1. Calcul du ratio (obligatoire pour ce modèle)
        ratio = fishing_hours / hours if hours > 0 else 0
        
        # 2. Préparation des données avec les 4 colonnes exactes
        data = pd.DataFrame(
            [[hours, fishing_hours, mmsi_present, ratio]], 
            columns=['hours', 'fishing_hours', 'mmsi_present', 'congestion_ratio']
        )
        
        # dmatrix = xgb.DMatrix(data)
        
        # # 3. Prédiction et extraction du score (Correction du tableau NumPy)
        # prediction = self.model.predict(dmatrix)
        # score = float(np.array(prediction).flatten()[0])
        
        # # 4. Mapping du score (Logique inversée selon tes tests de tout à l'heure)
        # # Rappel : Tes tests ont montré que score élevé (0.96) = Port Vide
        # if score > 0.7: 
        #     return "LOW"
        # elif score > 0.3: 
        #     return "MEDIUM"
        # else: 
        #     return "HIGH"
        dmatrix = xgb.DMatrix(data)
        prediction = self.model.predict(dmatrix)
        score = float(np.array(prediction).flatten()[0]) # On garde le score ici
        
        # Mapping du label
        if score > 0.7: label = "LOW"
        elif score > 0.3: label = "MEDIUM"
        else: label = "HIGH"
        
        # RETOURNE LES DEUX
        return label, score
    
# Instance unique chargée au démarrage du serveur
predictor = CongestionPredictor()