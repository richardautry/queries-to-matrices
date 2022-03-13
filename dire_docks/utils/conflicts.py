import numpy as np
from typing import List
from dire_docks.utils.matrices import Matrix
from dire_docks.models import CargoShip, CargoShipConflict
from django.db.models import Q, QuerySet

# TODO:
"""
Answer the question, is multiple queries to conflicts faster than
One query to in-memory conflict detection?
"""


# def find_conflicts(compare_matrix: Matrix, matrices: List[Matrix]):
#     for matrix in matrices:
#         if compare_matrix.detect_conflict(matrix):
#             compare_matrix.create_conflict(matrix)


def find_conflicts(cargo_ship: CargoShip, queryset: QuerySet):
    for query_ship in queryset.all():
        find_dock_depart_range_conflicts(cargo_ship, query_ship)
        find_cargo_ship_type_conflicts(cargo_ship, query_ship)


def find_dock_depart_range_conflicts(cargo_ship: CargoShip, compare_cargo_ship: CargoShip):
    if (
        cargo_ship.dock_time <= compare_cargo_ship.dock_time <= cargo_ship.depart_time or
        cargo_ship.dock_time <= compare_cargo_ship.depart_time <= cargo_ship.depart_time
    ):
        CargoShipConflict.objects.create(
            type="dock_depart_range",
            cargo_ship_a=cargo_ship,
            cargo_ship_b=compare_cargo_ship
        )


def find_cargo_ship_type_conflicts(cargo_ship: CargoShip, compare_cargo_ship: CargoShip):
    if cargo_ship.type == compare_cargo_ship.type:
        CargoShipConflict.objects.create(
            type="type_conflict",
            cargo_ship_a=cargo_ship,
            cargo_ship_b=compare_cargo_ship
        )


def find_conflicts_query(cargo_ship: CargoShip, queryset: QuerySet):
    find_dock_depart_range_conflicts_query(cargo_ship, queryset)
    find_cargo_ship_type_conflicts_query(cargo_ship, queryset)


def find_dock_depart_range_conflicts_query(cargo_ship: CargoShip, queryset: QuerySet):
    """
    Find conflicts where dock-to-depart ranges overlap.
    i.e. CargoShips should not be able to occupy the Dock as same time
    """
    conflict_query = queryset.filter(
        Q(dock_time__gte=cargo_ship.dock_time, dock_time__lte=cargo_ship.depart_time) |
        Q(depart_time__gte=cargo_ship.dock_time, depart_time__lte=cargo_ship.depart_time)
    )
    for query_ship in conflict_query.all():
        CargoShipConflict.objects.create(
            type="dock_depart_range",
            cargo_ship_a=cargo_ship,
            cargo_ship_b=query_ship
        )


def find_cargo_ship_type_conflicts_query(cargo_ship: CargoShip, queryset: QuerySet):
    """
    Find conflicts where two CargoShips of the same type are set to occupy a Dock.
    i.e. Should only be one of each type per Dock
    """
    conflict_query = queryset.filter(type=cargo_ship.type)
    for query_ship in conflict_query.all():
        CargoShipConflict.objects.create(
            type="type_conflict",
            cargo_ship_a=cargo_ship,
            cargo_ship_b=query_ship
        )


def find_conflicts_combined(cargo_ship: CargoShip, queryset: QuerySet):
    conflict_query = queryset.filter(
        Q(
            Q(dock_time__gte=cargo_ship.dock_time, dock_time__lte=cargo_ship.depart_time) |
            Q(depart_time__gte=cargo_ship.dock_time, depart_time__lte=cargo_ship.depart_time)
        ) |
        Q(type=cargo_ship.type)
    )
    find_conflicts(cargo_ship, conflict_query)
