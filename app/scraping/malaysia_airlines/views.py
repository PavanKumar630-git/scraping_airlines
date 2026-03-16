
import requests
from rest_framework.response import Response

from .controllers import *
from .serializers import *

from drf_yasg.utils import swagger_auto_schema


from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Malaysia Airlines"])
class MalaysiaViewer(viewsets.ViewSet):
    
    @extend_schema(summary="Malaysia Airlines",
        request=MalaysiaTokenDetails)
    @action(detail=False, methods=["post"], url_path="get-details")
    def login(self, request):
        serializer = MalaysiaTokenDetails(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = MalaysiaController.get_booking_details(serializer.validated_data)

        return Response(data)