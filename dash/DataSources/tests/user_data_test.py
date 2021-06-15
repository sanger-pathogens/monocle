from   unittest               import TestCase
from   unittest.mock          import patch
from   ldap                   import SERVER_DOWN
from   DataSources.user_data  import UserData, UserDataError

import logging
logging.basicConfig(format='%(asctime)-15s %(levelname)s:  %(message)s', level='CRITICAL')

class MonocleUserDataTest(TestCase):

   test_config          = 'DataSources/tests/mock_data/data_sources.yml'
   bad_config           = 'DataSources/tests/mock_data/data_sources_bad.yml'
   bad_openldap_config  = 'DataSources/tests/mock_data/openldap-bad.yaml'
   # in UserData object variable config (dict of config parames) the OpenLDAP params are stored using this key:
   openldap_config_key  = 'openldap'
   expected_config_str  = ['openldap_config', 'ldap_url', 'users_obj', 'groups_obj', 'username_attr',
                           'uid_attr', 'membership_attr', 'gid_attr', 'inst_id_attr', 'inst_name_attr']
   expected_ldap_str    = ['LDAP_ORGANISATION', 'LDAP_DOMAIN', 'LDAP_ADMIN_PASSWORD', 'LDAP_CONFIG_PASSWORD', 'LDAP_READONLY_USER_USERNAME',
                           'LDAP_READONLY_USER_PASSWORD', 'MONOCLE_LDAP_BASE_DN', 'MONOCLE_LDAP_BIND_DN', 'MONOCLE_LDAP_BIND_PASSWORD']
   expected_ldap_bool   = ['LDAP_READONLY_USER']
      
   mock_ldap_result_user      =  (  'cn=mock_username_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                    {  'cn': [b'mock_username_sanger_ac_uk'],
                                       'gidNumber': [b'501'],
                                       'homeDirectory': [b'/home/users/tmock_username_sanger_ac_uk'],
                                       'mail': [b'mock_username@sanger.ac.uk'],
                                       'o': [b'501', b'502'],
                                       'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                       'sn': [b'mock_username_sanger_ac_uk'],
                                       'uid': [b'mock_username'],
                                       'uidNumber': [b'1000']
                                       }
                                    )
   mock_ldap_result_user_no_o =  (  'cn=mock_username_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                    {  'cn': [b'mock_username_sanger_ac_uk'],
                                       'gidNumber': [b'501'],
                                       'homeDirectory': [b'/home/users/tmock_username_sanger_ac_uk'],
                                       'mail': [b'mock_username@sanger.ac.uk'],
                                       'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                       'sn': [b'mock_username_sanger_ac_uk'],
                                       'uid': [b'mock_username'],
                                       'uidNumber': [b'1000']
                                       }
                                    )
   mock_ldap_result_group     =  (  'cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                                    {  'cn': [b'WelSanIns'],
                                       'description': [b'Wellcome Sanger Institute'],
                                       'gidNumber': [b'501'],
                                       'objectClass': [b'posixGroup', b'top']
                                       }
                                    )

   def setUp(self):
      self.userdata = UserData(set_up=False)
      self.userdata.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.userdata, UserData)
      for this_expected_string in self.expected_config_str:
         this_value = self.userdata.config[this_expected_string]
         self.assertIsInstance(this_value, type('a string'))
      for this_expected_string in self.expected_ldap_str:
         this_value = self.userdata.config[self.openldap_config_key][this_expected_string]
         self.assertIsInstance(this_value, type('a string'))
      for this_expected_bool in self.expected_ldap_bool:
         this_value = self.userdata.config[self.openldap_config_key][this_expected_bool]
         self.assertIsInstance(this_value, type(True))

   def test_reject_bad_config(self):
      with self.assertRaises(KeyError):
         doomed = UserData(set_up=False)
         doomed.set_up(self.bad_config)
         
   def test_missing_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = UserData(set_up=False)
         doomed.set_up('no_such_config.yml')

   def test_reject_bad_ldap_config(self):
      with self.assertRaises(KeyError):
         doomed = UserData(set_up=False)
         doomed.read_openldap_config(self.bad_openldap_config)

   def test_missing_ldap_config(self):
      with self.assertRaises(FileNotFoundError):
         doomed = UserData(set_up=False)
         doomed.read_openldap_config('no_such.yaml')

   def test_low_level_search(self):
      with self.assertRaises(TypeError):
         self.userdata.ldap_search('inetOrgPerson','uid')
      with self.assertRaises(UserDataError):
         self.userdata.ldap_search('inetOrgPerson','uid',None)
      with self.assertRaises(UserDataError):
         self.userdata.ldap_search('inetOrgPerson','uid','')
      with self.assertRaises(SERVER_DOWN):
         self.userdata.ldap_search('inetOrgPerson','uid','this_is_valid')

   @patch.object(UserData, 'ldap_search')
   def test_user_search(self,mock_query):
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_group]
         user_ldap_result = self.userdata.ldap_search_user_by_username('')
      # expect single search result
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_user, self.mock_ldap_result_user]
         user_ldap_result = self.userdata.ldap_search_user_by_username('mock_username')
      # expect user record not group record
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_group]
         user_ldap_result = self.userdata.ldap_search_user_by_username('mock_username')
      # expect user record to include required attributes
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_user_no_o]
         user_ldap_result = self.userdata.ldap_search_user_by_username('mock_username')
      mock_query.return_value = [self.mock_ldap_result_user]
      user_ldap_result = self.userdata.ldap_search_user_by_username('mock_username')
      self.assertIsInstance(user_ldap_result, type(('a','tuple')))


   # TODO  as above, but ldap_search_group_by_gid()
   
   # TODO  get_user_details, testing data returned in expect structure

