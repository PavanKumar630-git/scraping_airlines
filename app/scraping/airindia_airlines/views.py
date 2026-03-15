
from rest_framework.response import Response

from .controllers import AirIndiaController
from .serializers import AirIndiaTokenDetails, AirIndiaSerializer


from drf_yasg.utils import swagger_auto_schema


from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["AirIndia Airlines"])
class AirIndiaViewer(viewsets.ViewSet):


    # @extend_schema(summary="AirIndia documents")
    # @action(detail=False, methods=["get"], url_path="scrape")
    # def scrape(self, request):

    #     data = AirIndiaController.scrape()

    #     return Response(data)
    
    
    # @extend_schema(summary="AirIndia",
    #     request=AirIndiaTokenDetails)
    # @action(detail=False, methods=["post"], url_path="login")
    # def login(self, request):
    #     serializer = AirIndiaTokenDetails(data=request.data)

    #     if not serializer.is_valid():
    #         return Response(serializer.errors, status=400)

    #     data = AirIndiaController.user_login(serializer.validated_data)

    #     return Response(data)
    
    @extend_schema(summary="AirIndia",
        request=AirIndiaTokenDetails)
    @action(detail=False, methods=["post"], url_path="get-details")
    def login(self, request):
        serializer = AirIndiaTokenDetails(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = AirIndiaController.get_booking_details(serializer.validated_data)

        return Response(data)