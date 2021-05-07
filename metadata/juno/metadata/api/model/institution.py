from dataclasses import dataclass


@dataclass
class Institution:
    name: str
    country: str
    latitude: float
    longitude: float
