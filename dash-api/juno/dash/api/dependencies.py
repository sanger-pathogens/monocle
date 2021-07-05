import os
import logging
from flask import Config
from injector import singleton, Module, provider

logger = logging.getLogger()


class DashboardApiModule(Module):
    """ Dependency injection handler for this API """

    # TODO: Add bindings into this class - see metadata api for examples

    API_TEST_MODE = False

    def __init__(self) -> None:
        try:
            self.API_TEST_MODE = os.environ['API_TEST_MODE'].lower() == 'true'
        except KeyError:
            pass

