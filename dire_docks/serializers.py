from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q
from dire_docks.utils.matrices import CargoShipMatrix
from dire_docks.utils.conflicts import find_conflicts, find_conflicts_query


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
        # TODO:
        """
        The basic idea works. Now we can think about the API/DX for `matrices.py` and `conflicts.py`

        1. we should be returning a label on the `...Conflict` object that indicates
        what TYPE of conflict was found (or which field is causing the conflict perhaps)

        2. We should be using a query for some conflict detection and matrix math for others
        Is there a speed difference?

        As an example, is it better to 5 db queries to determine conflicts, or 1 query and determines conflicts
        in memory via iteration
        """
        instance = super().create(validated_data)
        instance_matrix = CargoShipMatrix(instance)
        matrices = [CargoShipMatrix(obj) for obj in CargoShip.objects.filter(dock=instance.dock).exclude(Q(id=instance.id)).prefetch_related("dock")]
        find_conflicts(instance_matrix, matrices)
        # find_conflicts_query(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance_matrix = CargoShipMatrix(instance)
        instance_matrix.delete_conflicts()
        matrices = [CargoShipMatrix(obj) for obj in CargoShip.objects.exclude(Q(dock=None) | Q(id=instance.id))]
        find_conflicts(instance_matrix, matrices)
        return instance

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
    cargo_ships = CargoShipSerializer(many=True, read_only=True)

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
