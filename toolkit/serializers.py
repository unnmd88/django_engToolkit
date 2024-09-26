from rest_framework import serializers

from toolkit.models import ControllerManagement, TrafficLightObjects


class ControllerHostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControllerManagement
        fields = '__all__'

class TrafficLightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficLightObjects
        fields = '__all__'

