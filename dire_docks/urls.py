from rest_framework import routers
from dire_docks.views import DockViewSet, CaroShipViewSet

router = routers.DefaultRouter()
router.register(r'docks', DockViewSet)
router.register(r'cargo_ships', CaroShipViewSet)
