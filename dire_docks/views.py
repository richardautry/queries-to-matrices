from dire_docks.models import Dock, CargoShip, CargoShipConflict
from dire_docks.serializers import DockSerializer, CargoShipSerializer, CargoShipConflictSerializer
from rest_framework import viewsets


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
        super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # TODO: The attr we are looking for is `_prefetch_related_lookups (as viewed via debug)
        # We can use this to double check the prefetch_related vs. related objects to warn about
        # inefficiencies

        super().list(request, *args, **kwargs)


class CargoShipConflictViewSet(viewsets.ModelViewSet):
    queryset = CargoShipConflict.objects.all()
    serializer_class = CargoShipConflictSerializer
