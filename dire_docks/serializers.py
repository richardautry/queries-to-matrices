from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q


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
    dock_id = serializers.PrimaryKeyRelatedField(source='dock', queryset=Dock.objects.all(), required=False)
    conflicts = serializers.SerializerMethodField()

    def get_conflicts(self, obj):
        instances = CargoShipConflict.objects.filter(
            Q(cargo_ship_a__id=obj.id) | Q(cargo_ship_b__id=obj.id)
        )
        return [CargoShipConflictSerializer(instance).data for instance in instances]

    def create(self, validated_data):
        instance = super().create(validated_data)
        # TODO: Run `find_conflicts` here and check that returned object has conflicts included
        return instance

    def update(self, instance, validated_data):
        # TODO: Delete original conflicts and rerun `find_conflicts` here
        return super().update(instance, validated_data)

    class Meta:
        model = CargoShip
        fields = [
            'id',
            'name',
            'max_idle_time',
            'max_containers',
            'dock_time',
            'depart_time',
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
