from rest_framework import routers
from dire_docks.views import DockViewSet, CargoShipViewSet, CargoShipConflictViewSet

router = routers.DefaultRouter()
router.register(r'docks', DockViewSet)
router.register(r'cargo_ships', CargoShipViewSet)
router.register(r'cargo_ship_conflicts', CargoShipConflictViewSet)
