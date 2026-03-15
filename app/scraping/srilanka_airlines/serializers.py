
from rest_framework import serializers
from .models import LufhansaDocument

class SrilankaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LufhansaDocument
        fields = "__all__"

class SrilankaTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()