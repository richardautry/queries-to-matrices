from dire_docks.models import Dock, CargoShip, CargoShipConflict
from dire_docks.serializers import DockSerializer, CargoShipSerializer, CargoShipConflictSerializer
from rest_framework import viewsets
from django.db.models import ForeignKey


class DockViewSet(viewsets.ModelViewSet):
    queryset = Dock.objects.all().prefetch_related(
        "cargo_ships",
        "cargo_ships__cargo_ship_a_conflict",
        "cargo_ships__cargo_ship_b_conflict",
        "cargo_ships__cargo_ship_a_conflict__cargo_ship_a",
        "cargo_ships__cargo_ship_a_conflict__cargo_ship_b",
        "cargo_ships__cargo_ship_b_conflict__cargo_ship_a",
        "cargo_ships__cargo_ship_b_conflict__cargo_ship_b"
    )
    serializer_class = DockSerializer


class CargoShipViewSet(viewsets.ModelViewSet):
    # TODO: Optimize queryset to facilitate conflict detection
    queryset = CargoShip.objects.all().prefetch_related(
        "dock",
        "cargo_ship_a_conflict",
        "cargo_ship_b_conflict",
        "cargo_ship_a_conflict__cargo_ship_a",
        "cargo_ship_a_conflict__cargo_ship_b",
        "cargo_ship_b_conflict__cargo_ship_a",
        "cargo_ship_b_conflict__cargo_ship_b"
    )
    serializer_class = CargoShipSerializer
    # TODO: We have a model, queryset, and serializer. Can we we help detect query inefficiencies early?

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # TODO: The attr we are looking for is `_prefetch_related_lookups (as viewed via debug)
        # We can use this to double check the prefetch_related vs. related objects to warn about
        # inefficiencies
        print(self.serializer_class, self.queryset)
        print(self.serializer_class.Meta.model._meta.fields)
        print(self.serializer_class.Meta.model._meta.fields_map)
        print(self.queryset._prefetch_related_lookups)

        # TODO: The idea works. We can check for foreign fields being accounted for in prefetch_related.
        # Now, need to turn this into a function (possibly decorator) and issue logger warnings
        for field in self.serializer_class.Meta.model._meta.fields:
            if isinstance(field, ForeignKey):
                found_field = field.name in self.queryset._prefetch_related_lookups
                print(f"{field.name} in prefetch_related_lookups: {found_field}")

        for field_map in list(self.serializer_class.Meta.model._meta.fields_map.keys()):
            found_field_map = field_map in self.queryset._prefetch_related_lookups
            print(f"{field_map} in prefetch_related_lookups: {found_field_map}")

        return super().list(request, *args, **kwargs)


class CargoShipConflictViewSet(viewsets.ModelViewSet):
    queryset = CargoShipConflict.objects.all()
    serializer_class = CargoShipConflictSerializer
