from rest_framework import serializers
from dire_docks.models import Dock, CargoShip, CargoShipConflict
from django.db.models import Q
from dire_docks.utils.conflicts import find_conflicts


# TODO: Change name of project and repo to better reflect current state.
class CargoShipConflictSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if self.source == "cargo_ship_a_conflict":
            cargo_ship_id_field = "cargo_ship_b"
        else:
            cargo_ship_id_field = "cargo_ship_a"

        return {
            "parent_id": str(getattr(instance, cargo_ship_id_field).id),
            "type": instance.type
        }


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
        conflict_dict = {}

        conflict_a_queryset = obj.cargo_ship_a_conflict
        conflict_b_queryset = obj.cargo_ship_b_conflict
        if self.context['request'].method != 'GET':
            # In the case of POST/PUT/PATCH, prefetch related objects to reduce queries
            conflict_a_queryset = conflict_a_queryset.prefetch_related("cargo_ship_b")
            conflict_b_queryset = conflict_b_queryset.prefetch_related("cargo_ship_a")

        conflicts = CargoShipConflictSerializer(
            conflict_a_queryset,
            many=True,
            source="cargo_ship_a_conflict"
        ).data
        conflicts.extend(CargoShipConflictSerializer(
            conflict_b_queryset,
            many=True,
            source="cargo_ship_b_conflict"
        ).data)
        for conflict in conflicts:
            # combine conflicts into aggregated dict
            if conflict_dict.get(conflict["parent_id"]):
                conflict_dict[conflict["parent_id"]].append(conflict["type"])
            else:
                conflict_dict[conflict["parent_id"]] = [conflict["type"]]
        return conflict_dict

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
