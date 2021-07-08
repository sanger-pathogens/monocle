import connexion
import json
import os
import logging.config

#from flask_cors import CORS
from flask_injector import FlaskInjector


OPEN_API_SPEC_FILE = 'openapi.yml'


def create_application(conf_file: str, injection_bindings):
    """ Application configuration """

    use_swagger_ui = True if os.environ.get('ENABLE_SWAGGER_UI', '').lower() == 'true' else False

    # Create connexion flask application and load the open api REST specification file
    app_handle = connexion.FlaskApp(__name__, specification_dir='../interface', options={'swagger_ui': use_swagger_ui})
    app_handle.add_api(OPEN_API_SPEC_FILE, strict_validation=True)

    # Load configuration
    with open(conf_file) as config_file:
        app_handle.app.config.update(json.load(config_file))

    # Load logging configuration
    #logging.config.dictConfig(app_handle.app.config.get('logging_config'))
    app_handle.app.config['DEBUG'] = True

    # Turn off automatic ordering of JSON keys
    app_handle.app.config['JSON_SORT_KEYS'] = False

    # Setup Flask Injector
    FlaskInjector(app=app_handle.app, modules=[injection_bindings])

    # CORS setup
    # TODO Is this needed for dash api?
    #app_handle.app.config['CORS_HEADERS'] = 'Content-Type'
    #cors_regex = app_handle.app.config.get("cors")["regex"]
    #CORS(app_handle.app, resources={
    #    "/":
    #       {
    #            'origins': cors_regex
    #        }
    #})

    return app_handle
