from django_filters import rest_framework as filters
from dire_docks.models import CargoShip


class CargoShipFilter(filters.FilterSet):
    # name = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = CargoShip
        fields = ['name',]