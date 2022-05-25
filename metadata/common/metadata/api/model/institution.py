from dataclasses import dataclass


@dataclass
class Institution:
    name: str
    country: str
    latitute: float = None
    longitude: float = None
