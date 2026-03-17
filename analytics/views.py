from rest_framework.views import APIView
from rest_framework.response import Response
from .services import compute_congestion


class PortAnalyticsView(APIView):

    def get(self, request, port_id):

        level, boats_count = compute_congestion(port_id)

        return Response({"port_id": port_id,"boats_in_port": boats_count,"congestion_level": level})