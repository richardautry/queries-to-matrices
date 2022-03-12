from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q
from dire_docks.utils.matrices import CargoShipMatrix
from dire_docks.utils.conflicts import find_conflicts, find_cargo_ship_type_conflicts


class CargoShipConflictSerializer(serializers.ModelSerializer):
    cargo_ship_a_id = serializers.PrimaryKeyRelatedField(source="cargo_ship_a", read_only=True)
    cargo_ship_b_id = serializers.PrimaryKeyRelatedField(source="cargo_ship_b", read_only=True)

    class Meta:
        model = CargoShipConflict
        fields = [
            'id',
            'type',
            'cargo_ship_a_id',
            'cargo_ship_b_id'
        ]


class CargoShipSerializer(serializers.ModelSerializer):
    dock_id = serializers.PrimaryKeyRelatedField(source='dock', queryset=Dock.objects.all(), required=False)
    conflicts = serializers.SerializerMethodField()

    def get_conflicts(self, obj):
        return (
            # [conflict_a.id for conflict_a in obj.cargo_ship_a_conflict.all()] +
            # [conflict_b.id for conflict_b in obj.cargo_ship_b_conflict.all()]
            [CargoShipConflictSerializer(conflict_a).data for conflict_a in obj.cargo_ship_a_conflict.all()] +
            [CargoShipConflictSerializer(conflict_b).data for conflict_b in obj.cargo_ship_b_conflict.all()]
        )

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
        # TODO: We are likely starting with the same queryset in update and create. Where should this live?
        conflict_queryset = CargoShip.objects.filter(dock=instance.dock).exclude(id=instance.id).prefetch_related("dock")
        matrices = [CargoShipMatrix(obj) for obj in conflict_queryset.all()]
        # TODO: We are likely checking the same conflicts on update and create. Can we aggregate checks somewhere?
        find_conflicts(instance_matrix, matrices)
        find_cargo_ship_type_conflicts(cargo_ship=instance, queryset=conflict_queryset)
        # find_conflicts_query(instance)
        return instance

    def update(self, instance, validated_data):
        # TODO: To really complete this kind of demo, need to mirror conflict checks from `create` here
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
            'conflicts',
            'type'
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
