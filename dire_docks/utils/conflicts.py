import numpy as np
from typing import List
from dire_docks.utils.matrices import Matrix


def find_conflicts(compare_matrix: Matrix, matrices: List[Matrix]):
    for matrix in matrices:
        if compare_matrix.detect_conflict(matrix):
            compare_matrix.create_conflict(matrix)
