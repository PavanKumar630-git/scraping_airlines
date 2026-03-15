
import requests
from rest_framework.response import Response

from .controllers import LufhansaController
from .serializers import LufhansaSerializer, LufhansaTokenDetails

from drf_yasg.utils import swagger_auto_schema


from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Lufhansa Airlines"])
class LufhansaViewer(viewsets.ViewSet):
    
    @extend_schema(summary="Lufhansa Airlines",
        request=LufhansaTokenDetails)
    @action(detail=False, methods=["post"], url_path="get-details")
    def login(self, request):
        serializer = LufhansaTokenDetails(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = LufhansaController.get_booking_details(serializer.validated_data)

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