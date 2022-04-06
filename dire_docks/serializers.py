from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q
from dire_docks.utils.conflicts import find_conflicts


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
        """
        Get all conflicts that involve the current CargoShip and serialize as uuid: [conflict_type]
        i.e. if two conflict types were found with another object:
        {
            "1234_abc...": [
                "dock_depart_range",
                "type_conflict"
            ]
        }
        NOTE: Serializing conflicts slows down the response. Just ids is faster.
        """
        conflicts = {}
        cargo_ship_conflict_queryset = CargoShipConflict.objects.filter(
            # We need to query and prefetch both sides of the conflict relationship: a and b
            Q(cargo_ship_a=obj.id) | Q(cargo_ship_b=obj.id)
        ).prefetch_related("cargo_ship_a", "cargo_ship_b")
        for conflict in cargo_ship_conflict_queryset.all():
            if conflict.cargo_ship_a != obj:
                conflict_ship_id = conflict.cargo_ship_a.id
            else:
                conflict_ship_id = conflict.cargo_ship_b.id

            conflict_ship_id = str(conflict_ship_id)  # Convert UUID to str for serialization

            # We'll output an aggregated view of conflicts as a list of types PER object
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
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        CargoShipConflict.objects.filter(
            Q(cargo_ship_a=instance.id) | Q(cargo_ship_b=instance.id)
        ).prefetch_related("cargo_ship_a", "cargo_ship_b").delete()
        conflict_queryset = CargoShip.objects.filter(dock=instance.dock).exclude(id=instance.id).prefetch_related("dock")
        find_conflicts(cargo_ship=instance, queryset=conflict_queryset)
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
        ]
        prefetch_related_fields = [
            "cargo_ship_a_conflict",
            "cargo_ship_b_conflict",
            "cargo_ship_a_conflict__cargo_ship_a",
            "cargo_ship_a_conflict__cargo_ship_b",
            "cargo_ship_b_conflict__cargo_ship_a",
            "cargo_ship_b_conflict__cargo_ship_b"
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
