from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict


class CargoShipConflictSerializer(serializers.ModelSerializer):
    cargo_ship_a_id = serializers.PrimaryKeyRelatedField(queryset=CargoShip.objects.all(), required=True)
    cargo_ship_b_id = serializers.PrimaryKeyRelatedField(queryset=CargoShip.objects.all(), required=True)

    class Meta:
        model = CargoShipConflict
        fields = [
            'id',
            'cargo_ship_a_id',
            'cargo_ship_b_id'
        ]


class CargoShipSerializer(serializers.ModelSerializer):
    dock_id = serializers.PrimaryKeyRelatedField(queryset=Dock.objects.all(), required=False)
    conflicts = CargoShipConflictSerializer(many=True)

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        model = CargoShip
        fields = [
            'id',
            'name',
            'max_idle_time',
            'max_containers',
            'dock_id',
            'conflicts'
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
