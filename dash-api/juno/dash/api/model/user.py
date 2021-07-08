from dataclasses import dataclass
from typing import List
from dash.api.model.group import Group


@dataclass
class User:
    username: str
    groups: List[Group]
