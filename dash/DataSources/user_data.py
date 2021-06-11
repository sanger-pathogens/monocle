import copy
import ldap
import logging
import yaml


class UserDataError(Exception):
   """ exception when user data methods are called with invalid parameter(s) """
   pass

class UserData:
   """
   Methods for retrieving user data from the Monocle LDAP service.
   """
   
   data_sources_config           = 'data_sources.yml'
   data_source                   = 'monocle_ldap'
   data_source_config_file_param = 'openldap_config'
   required_config_params        = [   data_source_config_file_param,
                                       'ldap_url',
                                       'users_obj',
                                       'groups_obj',
                                       'username_attr',
                                       'uid_attr',
                                       'gid_attr',
                                       ]
   required_openldap_params      = [   'MONOCLE_LDAP_BASE_DN',
                                       'MONOCLE_LDAP_BIND_DN',
                                       'MONOCLE_LDAP_BIND_PASSWORD',
                                       ]
   # list OpenLDAP params here if they are to be excluded from logging
   openldap_secret_params        = [   'LDAP_ADMIN_PASSWORD',
                                       'LDAP_CONFIG_PASSWORD',
                                       'LDAP_READONLY_USER_PASSWORD',
                                       'MONOCLE_LDAP_BIND_PASSWORD',
                                       ]

   def __init__(self, set_up=True):
      """
      Constructor.  Reads config from default config file by default;
      pass set_up=False to prevent config being dong on instalation, and
      subsequently you can call set_up() to configure with a config file of your choice
      """
      self._current_ldap_connection   = None
      if set_up:
         self.set_up(self.data_sources_config)
         # for logging, copy the config and remoce secrets
         logged_config = copy.deepcopy(self.config)
         for this_secret in self.openldap_secret_params:
            logged_config['openldap'][this_secret] = 'SECRET'
         logging.info("read monocle LDAP config: {}".format(logged_config))

   def set_up(self, config_file_name):
      """
      read config from named file
      """
      with open(config_file_name, 'r') as file:
         data_sources = yaml.load(file, Loader=yaml.FullLoader)
         self.config = data_sources[self.data_source]
         for required_param in self.required_config_params:
            if not required_param in self.config:
               logging.error("data source config file {} does not provide the required paramter {}.{}".format(config_file_name,self.data_source,required_param))
               raise KeyError
         # OpenLDAP config is in a separate config file
         self.read_openldap_config(self.config[self.data_source_config_file_param])

   def read_openldap_config(self, config_file_name):
      """
      read OpenLDAP config from named file
      the default file will have been read if set_up() was called, but it can be called separately
      if you want to load db credentials from a different config file
      """
      logging.info("Reading OpenLDAP config from {}".format(config_file_name))
      with open(config_file_name, 'r') as file:
         openldap_config = yaml.load(file, Loader=yaml.FullLoader)
         for required_param in self.required_openldap_params:
            if not required_param in openldap_config:
               logging.error("OpenLDAP config file {} does not provide the required paramter {}".format(config_file_name,required_param))
               raise KeyError
         self.config['openldap'] = openldap_config

   def connection(self):
      """
      If already connected to LDAP server, returns the connection.
      If not connected, initializes LDAP connection, using URL from config value `ldap_url`, and returns the connection
      Stores instance of `ldap.ldapobject.SimpleLDAPObject` connection class as self.connection, and returns same.
      """
      if self._current_ldap_connection is None:
         logging.info("Connecting to LDAP server {}".format(self.config['ldap_url']))
         conn = ldap.initialize(self.config['ldap_url'])
         assert (isinstance(conn, ldap.ldapobject.SimpleLDAPObject)), "ldap.initialize was expected to return and instance of ldap.ldapobject.SimpleLDAPObject, not {}".format(conn)
         conn.simple_bind_s(self.config['openldap']['MONOCLE_LDAP_BIND_DN'], self.config['openldap']['MONOCLE_LDAP_BIND_PASSWORD'])
         self._current_ldap_connection = conn
      return self._current_ldap_connection
   
   def disconnect(self):
      """
      If currently connected to LDAP server, disconencts.
      Does nothing if already disconnected.
      """
      if self._current_ldap_connection is not None:
         self._current_ldap_connection = None

   def username_search(self, username):
      """
      Wraps ldap_search() with a username search for the value passed
      """
      logging.info('searching for username {}'.format(username))
      result_list = self.ldap_search(  self.config['users_obj'],
                                       self.config['username_attr'],
                                       username
                                       )
      # believe there should be only one hit -- or usernames aren't unique :-/
      if 1 < len(result_list):
         UserDataError("The username {} matched multiple entries in {}.{}:  it should be unique".format(username,self.config['users_obj'],self.config['username_attr']))
      result = result_list[0]
      # return value should be tuple with two elements
      #   1 the user's DN
      #   2 a dict with the attributes
      # we should always have a GID in the attributes
      if self.config['gid_attr'] not in result[1]:
         UserDataError("username {} search result doesn't seem to contain the required attribute {} (complete data = {})".format(username,self.config['gid_attr'],result))
      # TODO more validation to check user data are OK
      logging.debug("found user: {}".format(result))
      return result

   def gid_search(self, gid):
      """
      Wraps ldap_search() with a GID search for the value passed
      """
      logging.info('searching for GID {}'.format(gid))
      result_list = self.ldap_search(  self.config['groups_obj'],
                                       self.config['gid_attr'],
                                       gid
                                       )
      # should be only one hit -- or GID isn't unique :-/
      if 1 < len(result_list):
         UserDataError("The GID {} matched multiple entries in {}.{}:  it should be unique".format(gid,self.config['groups_obj'],self.config['gid_attr']))
      result = result_list[0]
      # TODO more validation to check group data are OK
      logging.debug("found group: {}".format(result))
      return result
   
   def ldap_search(self, object_class, attr, value):
      """
      Generic LDAP search method
      Searches for specified objects with attributes euqal to the given value, and returns whatever data is retrieved from LDAP
      """
      if value is not None and 0 < len(str(value)):
         UserDataError("LDAP search string must not be None and must not be an empty string")
      this_search = '(&(objectClass={})({}={}))'.format(object_class,attr,value)
      logging.info('LDAP search: {}'.format(this_search))
      # TODO add more graceful error handling
      result = self.connection().search_s(self.config['openldap']['MONOCLE_LDAP_BASE_DN'],
                                          ldap.SCOPE_SUBTREE,
                                          this_search
                                          )
      logging.debug("LDAP search result: {}".format(result))
      return result
