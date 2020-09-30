import os

from .common import *
from . import common

DEBUG = True
SECRET_KEY = "@7ad3g19au9^xhh3r&o^g!_g8h=%1di2&!ns&h*xy@tcqk#e9+"
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]
DATA_DIR = os.path.join(
    os.path.join(getattr(common, "BASE_DIR", None), os.pardir), "real-data/",
)
MOCK_DATA_DIR = os.path.join(
    os.path.join(getattr(common, "BASE_DIR", None), os.pardir), "mock-data/",
)
USE_MOCK_LANE_DATA = True

# uncomment the following to use mysql instead of sqlite3 during development
# (you will need to install and run mysql-server locally)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "monocle_local",
#         "USER": "root",
#         "PASSWORD": "",
#         "HOST": "127.0.0.1",
#         "PORT": "3306",
#     }
# }
