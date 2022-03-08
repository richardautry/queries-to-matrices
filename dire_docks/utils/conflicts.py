import numpy as np
from typing import List
from dire_docks.utils.matrices import Matrix
from dire_docks.models import CargoShip, CargoShipConflict
from django.db.models import Q, QuerySet


def find_conflicts(compare_matrix: Matrix, matrices: List[Matrix]):
    for matrix in matrices:
        if compare_matrix.detect_conflict(matrix):
            compare_matrix.create_conflict(matrix)


def find_conflicts_query(cargo_ship: CargoShip):
    conflict_query = CargoShip.objects.filter(
        dock=cargo_ship.dock
    )
    conflict_query = conflict_query.exclude(id=cargo_ship.id)
    conflict_query = conflict_query.filter(
        Q(dock_time__gte=cargo_ship.dock_time, dock_time__lte=cargo_ship.depart_time) |
        Q(depart_time__gte=cargo_ship.dock_time, depart_time__lte=cargo_ship.depart_time)
    )
    for query_ship in conflict_query.all():
        CargoShipConflict.objects.create(
            cargo_ship_a=cargo_ship,
            cargo_ship_b=query_ship
        )


def find_dock_time_conflicts(cargo_ship: CargoShip, queryset: QuerySet):
    # conflicts_query = queryset.
    pass