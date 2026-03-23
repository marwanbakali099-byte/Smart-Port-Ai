import os
import requests
import base64
from dotenv import load_dotenv
import cv2
import numpy as np
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

load_dotenv() # Charge les variables du fichier .env

# À la ligne 26, remplacez la chaîne de caractères par :
class SatelliteDetectionView(APIView):
    """
    Vue pour détecter des bateaux via Mapbox ou Upload, 
    utilisant Roboflow pour l'IA et OpenCV pour le dessin.
    """
    MAPBOX_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')

    def post(self, request):
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        file_obj = request.data.get('image')

        # 1. RÉCUPÉRATION DE L'IMAGE (MAPBOX OU UPLOAD)
        if lat and lon:
            mapbox_token = "pk.eyJ1IjoibWFyb3VhbmUtYmFrYWxpIiwiYSI6ImNtbXh3b21odjJ6bG4zMXNkajBidGRsYW0ifQ.3--VKM7KHXKxVX0jKhbeCQ" 
            zoom = 15  # Zoom optimisé pour Roboflow
            url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},{zoom},0/1024x1024?access_token={mapbox_token}"
            
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    return Response({"error": "Impossible de récupérer l'image Mapbox"}, status=400)
                image_content = response.content
                file_name = f"sat_{lat}_{lon}.jpg"
            except Exception as e:
                return Response({"error": f"Erreur Mapbox: {str(e)}"}, status=500)
        
        elif file_obj:
            image_content = file_obj.read()
            file_name = "uploaded_sat_image.jpg"
        else:
            return Response({"error": "Veuillez fournir 'lat'/'lon' ou une image"}, status=400)

        # 2. INFÉRENCE AVEC ROBOFLOW (CLOUD AI)
        # Encodage en Base64 pour l'API
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        
        # Configuration Roboflow (Seuil de confiance 20% comme dans ton Etape.txt)
        ROBOFLOW_API_KEY = "6FKjcs12ikSxvM11KzxW"
        ROBOFLOW_MODEL = "ship-detection-cojt4/1"
        rf_url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL}?api_key={ROBOFLOW_API_KEY}&confidence=20"

        try:
            rf_res = requests.post(
                rf_url, 
                data=image_base64, 
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            predictions = rf_res.json().get('predictions', [])
        except Exception as e:
            return Response({"error": f"Erreur Roboflow: {str(e)}"}, status=500)

        # 3. DESSIN DES RÉSULTATS AVEC OPENCV
        # Conversion du contenu binaire en image OpenCV
        nparr = np.frombuffer(image_content, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        detections_finales = []
        for p in predictions:
            # Calcul des coordonnées pour OpenCV (x,y centre -> x1,y1 coins)
            x1 = int(p['x'] - p['width'] / 2)
            y1 = int(p['y'] - p['height'] / 2)
            x2 = int(p['x'] + p['width'] / 2)
            y2 = int(p['y'] + p['height'] / 2)

            # Dessin du rectangle BLEU (BGR: 255, 0, 0)
            cv2.rectangle(img_cv2, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Ajout du texte "bateau"
            label = f"bateau {p['confidence']:.2f}"
            cv2.putText(img_cv2, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Stocker pour la réponse JSON
            detections_finales.append({
                "xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2,
                "conf": round(p['confidence'], 3)
            })

        # 4. SAUVEGARDE ET RÉPONSE
        # Sauvegarde de l'image modifiée dans le dossier media/tmp/
        relative_path = f'media/tmp/{file_name}'
        full_save_path = os.path.join(settings.BASE_DIR, relative_path)
        
        # S'assurer que le dossier existe
        os.makedirs(os.path.dirname(full_save_path), exist_ok=True)
        
        cv2.imwrite(full_save_path, img_cv2)

        return Response({
            "source": "Mapbox + Roboflow API",
            "count": len(detections_finales),
            "detections": detections_finales,
            "image_url": request.build_absolute_uri(settings.MEDIA_URL + f'tmp/{file_name}'),
            "coordinates": {"lat": lat, "lon": lon} if lat else None
        })

