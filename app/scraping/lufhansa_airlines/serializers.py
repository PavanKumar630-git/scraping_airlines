
from rest_framework import serializers
from .models import LufhansaDocument

class LufhansaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LufhansaDocument
        fields = "__all__"

class LufhansaTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()