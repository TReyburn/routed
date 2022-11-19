"""
Implementation of the Geocoder interface for interacting with
the Google Distance Matrix API
"""

import requests

from src.geocode.geocode import GeocoderInterface


class GoogleDistanceMatrix(GeocoderInterface):
    """Handles high level interfacing with the Google distance matrix API"""

    base_url: str = "https://maps.googleapis.com/maps/api/distancematrix/json?"

    def __init__(self, api_key: str):
        self.__api_key = api_key  # TODO: how should this be stored? b64 encode?
        self.unit_type = "imperial"  # TODO: make configurable with enum value type

    def geocode(self, addrs: list[str]) -> list[list[int]]:
        return [[]]

    def polyline(self, from_a: str, to_b: str) -> str:
        return ""

    # TODO: this isn't actually right. from_a and to_b are actually arrays
    #  as we can batch these calls by 100 elements each
    def _make_request(self, from_a: str, to_b: str) -> int:
        url = f"{self.base_url}units={self.unit_type}&origins={from_a}&destinations={to_b}&key={self.__api_key}"
        result = requests.get(url)
        match result.status_code:
            case 200:
                pass
            case 500:
                pass
        return 0
