"""Geocoder interface as an abstract base class"""
from abc import ABCMeta, abstractmethod
from typing import Any


class GeocoderInterface(metaclass=ABCMeta):
    """An abstract interface for classes which implement geocoding capabilities"""

    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        return callable(subclass.geocode) if hasattr(subclass, "geocode") else False

    @abstractmethod
    def geocode(self, addrs: list[str]) -> list[list[int]]:
        """Takes a list of addresses and turns them into a distance matrix"""
        raise NotImplementedError

    def polyline(self, from_a: str, to_b: str) -> str:
        """Creates a polyline representing the route from A to B"""
        raise NotImplementedError
