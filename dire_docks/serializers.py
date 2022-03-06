from rest_framework import serializers
from dire_docks.models import Dock, CargoShip


class CargoShipSerializer(serializers.ModelSerializer):
    dock_id = serializers.PrimaryKeyRelatedField(queryset=Dock.objects.all(), required=False)

    class Meta:
        model = CargoShip
        fields = [
            'id',
            'name',
            'max_idle_time',
            'max_containers',
            'dock_id'
        ]


class DockSerializer(serializers.ModelSerializer):
    cargo_ships = CargoShipSerializer(many=True)

    class Meta:
        model = Dock
        fields = [
            'id',
            'name',
            'open_time',
            'close_time',
            'max_ships',
            'cargo_ships'
        ]
        depth = 1
