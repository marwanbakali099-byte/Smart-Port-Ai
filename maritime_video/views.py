import cv2
import numpy as np
import streamlink
import time  # Importation propre du module temps
from datetime import datetime  # Importation propre du module date
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from ultralytics import YOLO

# Importe ton modèle BoatTraffic depuis le fichier models.py de ton app
from .models import BoatTraffic 

# Initialisation globale du modèle (chargé une seule fois)
video_model = YOLO('yolov8n.pt')
track_history = {}

class LivePortStreamView(APIView):
    """
    Vue pour le streaming temps réel avec détection, tracking et vitesse.
    """
    def get(self, request):
        # URL cible (Flux EarthCam ou lien direct .mp4)
        target_url = "https://www.earthcam.com/usa/california/losangeles/port/?cam=portofla"
        
        return StreamingHttpResponse(
            self.generate_stream(target_url),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )

    def generate_stream(self, url):
        try:
            streams = streamlink.streams(url)
            stream_url = streams['best'].url if 'best' in streams else url
        except Exception:
            stream_url = url

        cap = cv2.VideoCapture(stream_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reduce buffer size to prevent stale frames
        last_db_save = time.time() 
        frame_count = 0

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                
                frame_count += 1
                # Drop frames to maintain real-time sync (process 1 out of every 3 frames)
                if frame_count % 3 != 0:
                    continue

                # Resize image to significantly speed up YOLO inference
                frame = cv2.resize(frame, (640, 360))

                now = datetime.now()
                # Inférence YOLO avec Tracking (Classe 8 = bateau)
                results = video_model.track(frame, classes=[8], persist=True, verbose=False)

                if results[0].boxes.id is not None:
                    ids = results[0].boxes.id.cpu().numpy().astype(int)
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    confs = results[0].boxes.conf.cpu().numpy()

                    for id_boat, box, conf in zip(ids, boxes, confs):
                        x1, y1, x2, y2 = box
                        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

                        # --- CALCUL DE LA VITESSE ---
                        speed = 0
                        if id_boat in track_history:
                            prev_x, prev_y, prev_t = track_history[id_boat]
                            dt = (now - prev_t).total_seconds()
                            if dt > 0:
                                dist = np.sqrt((cx - prev_x)**2 + (cy - prev_y)**2)
                                speed = dist / dt # pixels par seconde
                        
                        track_history[id_boat] = (cx, cy, now)

                        # --- SAUVEGARDE EN BASE DE DONNÉES (SQL) ---
                        # On enregistre une ligne toutes les 3 secondes pour ne pas surcharger la DB
                        if time.time() - last_db_save > 3:
                            BoatTraffic.objects.create(
                                boat_id=int(id_boat),
                                speed=float(speed),
                                confidence=float(conf)
                            )
                            last_db_save = time.time()

                        # --- DESSIN SUR L'IMAGE ---
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(frame, f"ID:{id_boat} Spd:{speed:.1f}", (int(x1), int(y1)-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Encodage de l'image pour le flux HTTP avec qualité optimisée
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"CCTV Stream Error: {e}")
        finally:
            cap.release()

class BoatStatsView(APIView):
    """
    Vue pour renvoyer les statistiques des bateaux au format JSON pour le frontend.
    """
    def get(self, request):
        # Récupère les 15 dernières entrées
        stats = BoatTraffic.objects.all().order_by('-timestamp')[:15]
        
        data = []
        for s in stats:
            data.append({
                "id": s.boat_id,
                "vitesse": round(s.speed, 2),
                "heure": s.timestamp.strftime("%H:%M:%S"),
                "confiance": round(s.confidence * 100, 1)
            })
            
        return Response({
            "status": "success",
            "total_records": BoatTraffic.objects.count(),
            "last_detections": data
        })