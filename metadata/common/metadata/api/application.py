""" Methods for application initialisation """

import json
import logging.config
import os

import connexion
from flask import current_app
from flask_cors import CORS
from flask_injector import FlaskInjector

CORS_CONTEXT_REGEX = r"/metadata/*"
OPEN_API_SPEC_FILE = "openapi.yml"

logging_config = {
    "version": 1,
    "formatters": {"default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "root": {
        "level": "DEBUG" if not os.environ.get("LOG_LEVEL") else os.environ.get("LOG_LEVEL"),
        "handlers": ["wsgi"],
    },
}


def create_application(conf_file, injection_bindings):
    """Application configuration"""

    use_swagger_ui = True if os.environ.get("ENABLE_SWAGGER_UI", "").lower() == "true" else False

    # Create connexion flask application and load the open api REST specification file
    app_handle = connexion.FlaskApp(__name__, specification_dir="../interface", options={"swagger_ui": use_swagger_ui})
    app_handle.add_api(OPEN_API_SPEC_FILE, strict_validation=True)

    # Load configuration
    with open(conf_file) as config_file:
        app_handle.app.config.update(json.load(config_file))

    with app_handle.app.app_context():
        current_app.config = dict(app_handle.app.config)

    # Load logging configuration
    logging.config.dictConfig(logging_config)

    # Turn off automatic ordering of JSON keys
    app_handle.app.config["JSON_SORT_KEYS"] = False

    # Setup Flask Injector
    FlaskInjector(app=app_handle.app, modules=[injection_bindings])

    # CORS setup
    app_handle.app.config["CORS_HEADERS"] = "Content-Type"
    cors_regex = app_handle.app.config.get("cors")["regex"]
    CORS(app_handle.app, resources={CORS_CONTEXT_REGEX: {"origins": cors_regex}})

    return app_handle
