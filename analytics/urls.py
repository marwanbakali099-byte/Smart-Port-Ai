from django.urls import path
from .views import PortAnalyticsView

urlpatterns = [
    path("analytics/<int:port_id>/", PortAnalyticsView.as_view(),name="port-analytics"),
]