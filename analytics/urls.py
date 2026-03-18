from django.urls import path
from .views import BoatETAView, PortAnalyticsView, PortStatusView

urlpatterns = [
    path("analytics/<int:port_id>/", PortAnalyticsView.as_view(),name="port-analytics"),
    path("eta/<str:mmsi>/", BoatETAView.as_view(), name="boat-eta"),
    path('port/status/<int:port_id>/', PortStatusView.as_view(), name='port-status'),
]