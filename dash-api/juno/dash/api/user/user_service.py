from abc import ABC, abstractmethod
from dash.api.model.user import User


class UserDataError(Exception):
    """ Exception when user data methods queries or responses are not valid """
    pass


class UserService(ABC):
    """ Base class / interface for user data services """

    @abstractmethod
    def get_user_details(self, username: str) -> User:
        """ Return a list of institutions """
        pass
