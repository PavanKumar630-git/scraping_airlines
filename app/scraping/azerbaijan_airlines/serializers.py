
from rest_framework import serializers
from .models import LufhansaDocument

class AzerbaijanSerializer(serializers.ModelSerializer):
    class Meta:
        model = LufhansaDocument
        fields = "__all__"

class AzerbaijanTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()