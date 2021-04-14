from dataclasses import dataclass


@dataclass
class DbConnectionConfig:
    name: str
    connection_url: str
