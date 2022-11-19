"""Data models specific to Routing Internals"""
from dataclasses import dataclass


@dataclass
class InputDataModel:
    """InputDataModel"""

    distance_matrix: list[list[int]]
    num_vehicles: int
    depot_position: int


@dataclass
class OutputDataModel:
    """OutputDataModel"""

    path: list[int]
    distance: int


@dataclass
class RouteConstraints:
    """RouteConstraints"""

    # TODO: Name should be an enum of valid names
    name: str
    slack: int
    capacity: int
    fixed_start: bool = True
