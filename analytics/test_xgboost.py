import xgboost as xgb
import pandas as pd
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "xgboost_congestion_model.json")

def test_prediction():
    try:
        print(f"--- Chargement du modèle : {MODEL_PATH} ---")
        bst = xgb.Booster()
        bst.load_model(MODEL_PATH)
        print("✅ Modèle chargé avec succès.\n")

        # Scénarios : [hours, fishing_hours, mmsi_present]
        scenarios = [
            {"name": "Port Vide (Matin)", "data": [8, 0, 0]},
            {"name": "Activité Moyenne", "data": [12, 10, 5]},
            {"name": "Forte Congestion", "data": [18, 50, 20]},
        ]

        for s in scenarios:
            h, fh, m = s['data']
            ratio = fh / h if h > 0 else 0
            
            # Création du DataFrame avec les 4 colonnes attendues par le modèle
            df = pd.DataFrame([[h, fh, m, ratio]], 
                              columns=['hours', 'fishing_hours', 'mmsi_present', 'congestion_ratio'])
            
            dmat = xgb.DMatrix(df)
            
            prediction = bst.predict(dmat)
            
            # On utilise .item() ou .flatten() pour être sûr d'avoir un chiffre
            # cela règle l'erreur "0-dimensional arrays"
            score = float(np.array(prediction).flatten()[0]) 
            
            if score < 0.3:
                status = "LOW"
            elif score < 0.7:
                status = "MEDIUM"
            else:
                status = "HIGH"
                
            print(f"Scénario: {s['name']}")
            print(f" > Score IA: {score:.4f} | Résultat: {status}\n")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")

if __name__ == "__main__":
    test_prediction()