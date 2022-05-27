import logging.config
import os

import connexion
from dash.api.error_handlers import handle_unauthorised, handle_user_data_error
from dash.api.exceptions import NotAuthorisedException
from dash.api.service.DataSources.user_data import UserDataError

# from flask_cors import CORS


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


def create_application():
    """Application configuration"""

    use_swagger_ui = True if os.environ.get("ENABLE_SWAGGER_UI", "").lower() == "true" else False

    # Create connexion flask application and load the open api REST specification file
    app_handle = connexion.FlaskApp(__name__, specification_dir="../interface", options={"swagger_ui": use_swagger_ui})
    app_handle.add_api(OPEN_API_SPEC_FILE, strict_validation=True)

    # Load logging configuration
    logging.config.dictConfig(logging_config)

    # Add error handlers
    app_handle.add_error_handler(NotAuthorisedException, handle_unauthorised)
    app_handle.add_error_handler(UserDataError, handle_user_data_error)

    # Turn off automatic ordering of JSON keys
    app_handle.app.config["JSON_SORT_KEYS"] = False

    # CORS setup
    # TODO Is this needed for dash api?
    # app_handle.app.config['CORS_HEADERS'] = 'Content-Type'
    # cors_regex = app_handle.app.config.get("cors")["regex"]
    # CORS(app_handle.app, resources={
    #    "/":
    #       {
    #            'origins': cors_regex
    #        }
    # })

    return app_handle
