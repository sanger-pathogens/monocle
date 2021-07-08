import logging
from flask import Config
from dash.api.model.ldap_config import LdapConfig

logger = logging.getLogger()

LDAP_CONFIG_KEY = 'monocle_ldap'


def read_ldap_config(config: Config) -> LdapConfig:
    """ Return LDAP configuration """
    try:
        conf_params = config[LDAP_CONFIG_KEY]
    except KeyError as e:
        logger.error('Unable to find configuration key {}'.format(LDAP_CONFIG_KEY))
        raise e
    return LdapConfig(conf_params)
