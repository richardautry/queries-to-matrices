from dire_docks.models import Dock, CargoShip
from dire_docks.serializers import DockSerializer, CargoShipSerializer
from rest_framework import viewsets


class DockViewSet(viewsets.ModelViewSet):
    queryset = Dock.objects.all()
    serializer_class = DockSerializer


class CaroShipViewSet(viewsets.ModelViewSet):
    queryset = CargoShip.objects.all()
    serializer_class = CargoShipSerializer
