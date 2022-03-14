from dire_docks.models import Dock, CargoShip, CargoShipConflict
from dire_docks.serializers import DockSerializer, CargoShipSerializer, CargoShipConflictSerializer
from rest_framework import viewsets
from django.db.models import ForeignKey
from dire_docks.utils.views import check_prefetch_related


@check_prefetch_related
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


@check_prefetch_related
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


class CargoShipConflictViewSet(viewsets.ModelViewSet):
    queryset = CargoShipConflict.objects.all()
    serializer_class = CargoShipConflictSerializer
