from juno.settings.common import *

# TODO: Set production SECRET_KEY
# TODO: Set production CORS_ORIGIN_WHITELIST

DEBUG = False
SECRET_KEY = "@7ad3g19au9^xhh3r&o^g!_g8h=%1di2&!ns&h*xy@tcqk#e9+"
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "monocle.dev.pam.sanger.ac.uk",
]
DATA_DIR = "/data"
USE_MOCK_LANE_DATA = False
