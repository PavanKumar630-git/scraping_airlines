
from rest_framework import serializers
from .models import LufhansaDocument

class LotPolishSerializer(serializers.ModelSerializer):
    class Meta:
        model = LufhansaDocument
        fields = "__all__"

class LotPolishTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()