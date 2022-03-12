from dire_docks.models import Dock, CargoShip, CargoShipConflict
from dire_docks.serializers import DockSerializer, CargoShipSerializer, CargoShipConflictSerializer
from rest_framework import viewsets


class DockViewSet(viewsets.ModelViewSet):
    queryset = Dock.objects.all().prefetch_related(
        "cargo_ships",
        "cargo_ships__cargo_ship_a_conflict",
        "cargo_ships__cargo_ship_b_conflict",
    )
    serializer_class = DockSerializer


class CargoShipViewSet(viewsets.ModelViewSet):
    queryset = CargoShip.objects.all()
    serializer_class = CargoShipSerializer


class CargoShipConflictViewSet(viewsets.ModelViewSet):
    queryset = CargoShipConflict.objects.all()
    serializer_class = CargoShipConflictSerializer
