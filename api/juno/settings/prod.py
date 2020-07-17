import environ
from juno.settings.common import *

# TODO: Set production CORS_ORIGIN_WHITELIST

env = environ.Env()

DEBUG = False
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", env("HOSTNAME")]
DATA_DIR = "/data"
USE_MOCK_LANE_DATA = False
