from dire_docks.models import Dock, CargoShip, CargoShipConflict
from dire_docks.serializers import DockSerializer, CargoShipSerializer, CargoShipConflictSerializer
from rest_framework import viewsets, mixins
from dire_docks.utils.views import check_prefetch_related
from dire_docks.filters import CargoShipFilter
from django_filters import rest_framework as filters


@check_prefetch_related
class DockViewSet(viewsets.ModelViewSet):
    queryset = Dock.objects.prefetch_related(
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
    queryset = CargoShip.objects.prefetch_related(
        "dock",
        "cargo_ship_a_conflict__cargo_ship_a",
        "cargo_ship_a_conflict__cargo_ship_b",
        "cargo_ship_b_conflict__cargo_ship_a",
        "cargo_ship_b_conflict__cargo_ship_b",
    )
    serializer_class = CargoShipSerializer
    filterset_class = CargoShipFilter


class CargoShipConflictViewSet(viewsets.ModelViewSet):
    queryset = CargoShipConflict.objects
    serializer_class = CargoShipConflictSerializer
