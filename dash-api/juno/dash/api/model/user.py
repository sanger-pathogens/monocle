from dataclasses import dataclass
from dash.api.model.group import Group


@dataclass
class User:
    username: str
    groups: list[Group]
