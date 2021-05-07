import logging
import configparser
from flask import Config
from urllib.parse  import quote as urlencode
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition

logger = logging.getLogger()

MONOCLE_CONNECTION_FILE_PROPERTY = 'monocle_database_config_file'


def read_database_connection_config(config: Config) -> DbConnectionConfig:
    """ Load database connection settings from file """

    logger.info("Loading database connection details")

    connection_details_file = config[MONOCLE_CONNECTION_FILE_PROPERTY]

    if connection_details_file.strip() == "":
        raise RuntimeError('ERROR: {} configuration property is invalid'.format(MONOCLE_CONNECTION_FILE_PROPERTY))

    try:
        # Make sure we can open the file
        open(connection_details_file).close()

        db_config = configparser.ConfigParser()
        db_config.read(connection_details_file)

        password = db_config['client']['password'].strip('"')
        if password:
            url = "mysql://{}:{}@{}:{}/{}".format(db_config['client']['user'],
                                                  urlencode(password),
                                                  db_config['client']['host'],
                                                  db_config['client']['port'],
                                                  db_config['client']['database'],
                                                  )
        else:
            url = "mysql://{}@{}:{}/{}".format(db_config['client']['user'],
                                                db_config['client']['host'],
                                                db_config['client']['port'],
                                                db_config['client']['database'],
                                                )

        config = DbConnectionConfig('monocle', url)
        logger.info("Database connection details loaded")

        return config

    except FileNotFoundError as e:
        logger.error("ERROR: Unable to access the database connection details file")
        raise e
    except KeyError as ke:
        logger.error("ERROR: Missing property in database connection details file: " + str(ke))
        raise ke


def read_mock_database_connection_config(config: Config) -> DbConnectionConfig:
    """ Create dummy database connection settings """
    return DbConnectionConfig('monocle', None)


def read_spreadsheet_definition_config(config: Config) -> SpreadsheetDefinition:
    return SpreadsheetDefinition(config['spreadsheet_definition'])
