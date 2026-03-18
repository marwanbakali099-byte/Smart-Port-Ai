import joblib
import os
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, 'ais', 'eta_tanger_model.pkl')

MODEL = joblib.load(MODEL_PATH)

if isinstance(MODEL, dict):
    MODEL = MODEL['model']