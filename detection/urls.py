from rest_framework.routers import DefaultRouter
from .views import DetectionViewSet

router = DefaultRouter()
router.register(r"detections", DetectionViewSet)

urlpatterns = router.urls