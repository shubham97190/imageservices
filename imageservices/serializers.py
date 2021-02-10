from rest_framework import serializers

class GetImageSerializer(serializers.Serializer):
   """Your data serializer, define your fields here."""
   image = serializers.CharField()