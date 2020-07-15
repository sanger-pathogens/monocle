import os

from juno.settings.common import *
from juno.settings import common

DEBUG = True
SECRET_KEY = "@7ad3g19au9^xhh3r&o^g!_g8h=%1di2&!ns&h*xy@tcqk#e9+"
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
DATA_DIR = os.path.join(
    os.path.join(getattr(common, "BASE_DIR", None), os.pardir), "mock-data/",
)
USE_MOCK_LANE_DATA = True
