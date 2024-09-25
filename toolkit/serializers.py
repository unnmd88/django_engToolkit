from rest_framework.serializers import ModelSerializer

from toolkit.models import ControllerManagement


class ControllerHostsSerializer(ModelSerializer):
    class Meta:
        model = ControllerManagement
        fields = '__all__'

