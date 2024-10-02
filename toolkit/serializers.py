from rest_framework import serializers

from toolkit.models import ControllerManagement, TrafficLightObjects


class ControllerHostsSerializer(serializers.ModelSerializer):
    # data = serializers.ManyRelatedField(many=True)
    # data = serializers.SerializerMethodField()
    # edits = serializers.EditItemSerializer(many=True)
    # data = serializers.CharField
    class Meta:
        print(f'Meta ControllerHostsSerializer')

        model = ControllerManagement
        fields = '__all__'


class TrafficLightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficLightObjects
        fields = '__all__'

