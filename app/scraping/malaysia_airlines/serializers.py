
from rest_framework import serializers
from .models import LufhansaDocument

class MalaysiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LufhansaDocument
        fields = "__all__"

class MalaysiaTokenDetails(serializers.Serializer):
    pnr = serializers.CharField()
    last_name = serializers.CharField()