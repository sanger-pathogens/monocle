import logging
from copy import deepcopy

import ldap
import yaml
from dash.api.exceptions import LdapDataError

DATA_SOURCES_CONFIG = "data_sources.yml"
OPENLDAP_CONFIC_FILE_CONFIG_KEY = "openldap_config"
DATA_SOURCE = "monocle_ldap"
MIN_REQUIRED_CONFIG_PARAMS = [
    "openldap_config",
    "ldap_url",
    "gid_attr",
]
OPENLDAP_PARAMS_REQUIRED = [
    "MONOCLE_LDAP_BASE_DN",
    "MONOCLE_LDAP_BIND_DN",
    "MONOCLE_LDAP_BIND_PASSWORD",
]
# list OpenLDAP params here if they are to be excluded from logging
OPENLDAP_PARAMS_SECRET = [
    "LDAP_ADMIN_PASSWORD",
    "LDAP_CONFIG_PASSWORD",
    "LDAP_READONLY_USER_PASSWORD",
    "MONOCLE_LDAP_BIND_PASSWORD",
]


class LdapData:
    def __init__(self, required_attributes, set_up=True):
        self._current_ldap_connection = None
        self.required_config_params = MIN_REQUIRED_CONFIG_PARAMS + required_attributes

        if set_up:
            self.set_up(DATA_SOURCES_CONFIG)
            # for logging, copy the config and remoce secrets
            logged_config = deepcopy(self.config)
            for this_secret in OPENLDAP_PARAMS_SECRET:
                logged_config["openldap"][this_secret] = "SECRET"
            logging.info("read monocle LDAP config: {}".format(logged_config))

    def set_up(self, config_file_name):
        """
        read config from named file and check presence of required parameters in the file
        """
        with open(config_file_name, "r") as file:
            data_sources = yaml.load(file, Loader=yaml.FullLoader)
        self.config = data_sources[DATA_SOURCE]
        for required_param in self.required_config_params:
            if required_param not in self.config:
                logging.error(
                    "data source config file {} does not provide the required parameter {}.{}".format(
                        config_file_name, DATA_SOURCE, required_param
                    )
                )
                raise KeyError
        # OpenLDAP config is in a separate config file
        self.read_openldap_config(self.config[OPENLDAP_CONFIC_FILE_CONFIG_KEY])

    def read_openldap_config(self, config_file_name):
        """
        read OpenLDAP config from named file
        the default file will have been read if set_up() was called, but it can be called separately
        if you want to load db credentials from a different config file
        """
        logging.info("Reading OpenLDAP config from {}".format(config_file_name))
        with open(config_file_name, "r") as file:
            openldap_config = yaml.load(file, Loader=yaml.FullLoader)
        for required_param in OPENLDAP_PARAMS_REQUIRED:
            if required_param not in openldap_config:
                logging.error(
                    "OpenLDAP config file {} does not provide the required parameter {}".format(
                        config_file_name, required_param
                    )
                )
                raise KeyError
        self.config["openldap"] = openldap_config

    def connection(self):
        """
        If already connected to LDAP server, returns the connection.
        If not connected, initializes LDAP connection, using URL from config value `ldap_url`, and returns the connection
        Stores instance of `ldap.ldapobject.SimpleLDAPObject` connection class as self.connection, and returns same.
        """
        if self._current_ldap_connection is None:
            logging.info("Connecting to LDAP server {}".format(self.config["ldap_url"]))
            conn = ldap.initialize(self.config["ldap_url"])
            assert isinstance(
                conn, ldap.ldapobject.SimpleLDAPObject
            ), "ldap.initialize was expected to return an instance of ldap.ldapobject.SimpleLDAPObject, not {}".format(
                conn
            )
            conn.simple_bind_s(
                self.config["openldap"]["MONOCLE_LDAP_BIND_DN"], self.config["openldap"]["MONOCLE_LDAP_BIND_PASSWORD"]
            )
            self._current_ldap_connection = conn
        return self._current_ldap_connection

    def disconnect(self):
        """
        If currently connected to LDAP server, disconnects.
        Does nothing if already disconnected.
        """
        if self._current_ldap_connection is not None:
            self._current_ldap_connection = None

    def ldap_search_group_by_gid(self, gid, group_object_config_key):
        """
        Wraps ldap_search() adding params for search for a group using the GID value passed.
        Returns LDAP group record for the group if found, None if not found.
        Returns None if no match; raises LdapDataError if more than 1 match (GID should be unique)
        or if returned data are not valid for a group record.
        LDAP record expected to be a tuple with two elements
        - the group's DN
        - a dict of attributes
        Note attribute valids are bytes, require decode() to convert to string
        """
        logging.debug("searching for GID {}".format(gid))
        result_list = self.ldap_search(self.config[group_object_config_key], self.config["gid_attr"], gid)
        if 0 == len(result_list):
            return None
        if len(result_list) > 1:
            logging.error(
                "The GID {} matched multiple entries in {}.{}:  it should be unique".format(
                    gid, self.config[group_object_config_key], self.config["gid_attr"]
                )
            )
            raise LdapDataError("GID {} is not unique".format(gid))
        result = result_list[0]
        group_attr = result[1]
        for required_attr in [
            self.config["inst_id_attr"],
            self.config["inst_name_attr"],
            self.config["country_names_attr"],
        ]:
            if required_attr not in group_attr or len(group_attr[required_attr]) < 1:
                logging.error(
                    "group with GID {} doesn't seem to contain the required attribute {} (complete data = {})".format(
                        gid, required_attr, result
                    )
                )
                raise LdapDataError("group {} doesn't contain the required attribute {}".format(gid, required_attr))
        logging.debug("found group: {}".format(result))
        return result

    def ldap_search(self, object_class, attr, value):
        """
        Generic LDAP search method
        Searches for specified objects with attributes equal to the given value, and returns whatever data is retrieved from LDAP
        """
        if value is None or len(str(value)) < 1:
            raise LdapDataError("LDAP search string must not be None and must not be an empty string")
        this_search = "(&(objectClass={})({}={}))".format(object_class, attr, value)
        logging.debug("LDAP search: {}".format(this_search))
        # FIXME add more graceful error handling
        result = self.connection().search_s(
            self.config["openldap"]["MONOCLE_LDAP_BASE_DN"], ldap.SCOPE_SUBTREE, this_search
        )
        logging.debug("LDAP search result: {}".format(result))
        return result
