
import requests
from rest_framework.response import Response

from .controllers import SrilankaController
from .serializers import SrilankaSerializer, SrilankaTokenDetails

from drf_yasg.utils import swagger_auto_schema


from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Srilanka Airlines"])
class SriLankaViewer(viewsets.ViewSet):
    
    @extend_schema(summary="SriLanka Airlines",
        request=SrilankaTokenDetails)
    @action(detail=False, methods=["post"], url_path="get-details")
    def login(self, request):
        serializer = SrilankaTokenDetails(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = SrilankaController.get_booking_details(serializer.validated_data)

        return Response(data)
    

    # @action(detail=False, methods=["get"], url_path="get-tokens")
    # def get_session(self, request):

    #     session = requests.Session()

    #     headers = {
    #         "User-Agent": "Mozilla/5.0"
    #     }

    #     response = session.get("https://shop.lufthansa.com", headers=headers)

    #     cookies = session.cookies.get_dict()

    #     return Response({
    #         "status": "success",
    #         "cookies": cookies
    #     })