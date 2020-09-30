import environ
from .common import *

# TODO: Set production CORS_ORIGIN_WHITELIST

env = environ.Env()

DEBUG = False
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", env("HOSTNAME")]
DATA_DIR = "/data"
USE_MOCK_LANE_DATA = False

# my.cnf mounted from file on openstack vm
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {"read_default_file": "/etc/mysql/my.cnf"},
    }
}
