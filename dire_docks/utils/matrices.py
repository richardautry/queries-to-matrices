"""
Represent objects as matrices ideally from json to matrix (numpy array)
"""
import numpy as np
from dire_docks.models import CargoShip, CargoShipConflict
from django.db import models


class Matrix:
    def __init__(self):
        self.array = np.array([])
        self.instance = None
        self.conflict_class: [models.Model, None] = None

    def detect_conflict(self, obj: 'Matrix'):
        """
        Ex. [10, 20] and [15, 30]
        """
        dimensional_conflicts = []
        for i, dim in enumerate(self.array):
            if (
                    dim[0] <= obj.array[i][0] <= dim[1] or
                    dim[0] <= obj.array[i][1] <= dim[1]
            ):
                dimensional_conflicts.append(True)
            else:
                dimensional_conflicts.append(False)
        # Conflicts must be found on all dimensions to be considered overlap/conflict
        return all(dimensional_conflicts)

    def create_conflict(self, obj: 'Matrix'):
        """
        Create a conflict object that ties the two objects in conflict together
        """
        raise NotImplementedError


class CargoShipMatrix(Matrix):
    def __init__(self, cargo_ship_instance: CargoShip):
        """
        Tightly couple CargoShip to a numpy array format for comparisons
        """
        super().__init__()
        self.instance = cargo_ship_instance
        self.array = np.array([
            [int(cargo_ship_instance.dock.id)] * 2,
            [cargo_ship_instance.dock_time, cargo_ship_instance.depart_time]
        ])
        self.conflict_class = CargoShipConflict

    def detect_conflict(self, obj: 'CargoShipMatrix'):
        return super().detect_conflict(obj)

    def create_conflict(self, obj: 'CargoShipMatrix'):
        self.conflict_class.objects.create(
            cargo_ship_a=self.instance.id,
            cargo_ship_b=obj.instance.id
        )

