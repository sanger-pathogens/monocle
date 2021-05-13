import logging
import configparser
from flask import Config
from urllib.parse  import quote as urlencode
from metadata.api.model.db_connection_config import DbConnectionConfig
from metadata.api.model.spreadsheet_definition import SpreadsheetDefinition

logger = logging.getLogger()

MONOCLE_CONNECTION_FILE_PROPERTY = 'monocle_database_config_file'
DB_CONFIG_TAG = 'client'


def read_database_connection_config(config: Config) -> DbConnectionConfig:
    """ Load database connection settings from file """

    logger.info("Loading database connection details")

    password = None
    connection_details_file = config[MONOCLE_CONNECTION_FILE_PROPERTY]

    if connection_details_file.strip() == "":
        raise RuntimeError('ERROR: {} configuration property is invalid'.format(MONOCLE_CONNECTION_FILE_PROPERTY))

    try:
        # Make sure we can open the file
        open(connection_details_file).close()

        db_config = configparser.ConfigParser()
        db_config.read(connection_details_file)

        try:
            password = db_config[DB_CONFIG_TAG]['password'].strip('"')
        except KeyError:
            pass

        if password:
            url = "mysql://{}:{}@{}:{}/{}".format(db_config[DB_CONFIG_TAG]['user'],
                                                  urlencode(password),
                                                  db_config[DB_CONFIG_TAG]['host'],
                                                  db_config[DB_CONFIG_TAG]['port'],
                                                  db_config[DB_CONFIG_TAG]['database'],
                                                  )
        else:
            # No password provided
            url = "mysql://{}@{}:{}/{}".format(db_config[DB_CONFIG_TAG]['user'],
                                               db_config[DB_CONFIG_TAG]['host'],
                                               db_config[DB_CONFIG_TAG]['port'],
                                               db_config[DB_CONFIG_TAG]['database'],
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
    try:
        header_pos = int(config['spreadsheet_header_row_position'])
        if header_pos <= 0:
            raise (ValueError())
    except ValueError:
        raise(ValueError('spreadsheet_header_row_position value must be a positive integer'))

    return SpreadsheetDefinition(header_pos, config['spreadsheet_definition'])
