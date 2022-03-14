from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q
from dire_docks.utils.matrices import CargoShipMatrix
from dire_docks.utils.conflicts import find_conflicts, find_conflicts_query, find_conflicts_combined


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
    # conflicting_cargo_ships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    def get_conflicts(self, obj):
        """
        Get all conflicts that involve the current CargoShip
        NOTE: Serializing conflicts slows down the response. Just ids is faster.
        """
        conflicts = {}
        for conflict in list(obj.cargo_ship_a_conflict.all()) + list(obj.cargo_ship_b_conflict.all()):
            if conflict.cargo_ship_a != obj:
                conflict_ship_id = conflict.cargo_ship_a.id
            else:
                conflict_ship_id = conflict.cargo_ship_b.id

            conflict_ship_id = str(conflict_ship_id)  # Convert UUID to str for serialization

            if conflicts.get(conflict_ship_id):
                conflicts[conflict_ship_id].append(conflict.type)
            else:
                conflicts[conflict_ship_id] = [conflict.type]
        return conflicts

    def create(self, validated_data):
        instance = super().create(validated_data)
        # TODO: We are likely starting with the same queryset in update and create. Where should this live?
        conflict_queryset = CargoShip.objects.filter(dock=instance.dock).exclude(id=instance.id).prefetch_related("dock")
        find_conflicts(cargo_ship=instance, queryset=conflict_queryset)
        # find_conflicts_query(instance, conflict_queryset)
        # find_conflicts_combined(instance, conflict_queryset)
        # TODO: now, how to handle the conflicts from the requester's side?
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
            'type',
            # 'conflicting_cargo_ships'
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
