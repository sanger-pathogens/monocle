import os
import logging
from flask import Config
from injector import singleton, Module, provider
from dash.api.configuration import read_ldap_config
from dash.api.user.user_service import UserService
from dash.api.user.ldap_user_service import LdapUserService


logger = logging.getLogger()


class ApiModule(Module):
    """ Dependency injection handler for this API """

    # TODO: Add bindings into this class

    API_TEST_MODE = False

    def __init__(self) -> None:
        try:
            self.API_TEST_MODE = os.environ['API_TEST_MODE'].lower() == 'true'
        except KeyError:
            pass

    @provider
    @singleton
    def user_service(self, config: Config) -> UserService:
        return LdapUserService(read_ldap_config(config))
