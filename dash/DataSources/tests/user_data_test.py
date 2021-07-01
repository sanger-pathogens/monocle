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
      
   mock_ldap_result_user            =  (  'cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                          {  'cn': [b'mock_user_sanger_ac_uk'],
                                             'gidNumber': [b'501'],
                                             'homeDirectory': [b'/home/users/tmock_user_sanger_ac_uk'],
                                             'mail': [b'mock_user@sanger.ac.uk'],
                                             'o': [b'501', b'502'],
                                             'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                             'sn': [b'mock_user_sanger_ac_uk'],
                                             'uid': [b'mock_user'],
                                             'uidNumber': [b'1000']
                                             }
                                          )
   mock_ldap_result_user_no_o       =  (  'cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                          {  'cn': [b'mock_user_sanger_ac_uk'],
                                             'gidNumber': [b'501'],
                                             'homeDirectory': [b'/home/users/tmock_user_sanger_ac_uk'],
                                             'mail': [b'mock_user@sanger.ac.uk'],
                                             'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                             'sn': [b'mock_user_sanger_ac_uk'],
                                             'uid': [b'mock_user'],
                                             'uidNumber': [b'1000']
                                             }
                                          )
   mock_ldap_result_user_empty_o    =  (  'cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
                                          {  'cn': [b'mock_user_sanger_ac_uk'],
                                             'gidNumber': [b'501'],
                                             'homeDirectory': [b'/home/users/tmock_user_sanger_ac_uk'],
                                             'mail': [b'mock_user@sanger.ac.uk'],
                                             'o': [],
                                             'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                                             'sn': [b'mock_user_sanger_ac_uk'],
                                             'uid': [b'mock_user'],
                                             'uidNumber': [b'1000']
                                             }
                                          )
   mock_ldap_result_group           =  (  'cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                                          {  'cn': [b'WelSanIns'],
                                             'description': [b'Wellcome Sanger Institute'],
                                             'gidNumber': [b'501'],
                                             'objectClass': [b'posixGroup', b'top']
                                             }
                                          )
   mock_ldap_result_group_no_desc   =  (  'cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                                          {  'cn': [b'WelSanIns'],
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
      # reject multiple search results
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_user, self.mock_ldap_result_user]
         user_ldap_result = self.userdata.ldap_search_user_by_username('any_valid_string')
      # reject user record not group record
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_group]
         user_ldap_result = self.userdata.ldap_search_user_by_username('any_valid_string')
      # reject user record without required attributes
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_user_no_o]
         user_ldap_result = self.userdata.ldap_search_user_by_username('any_valid_string')
      # TODO this method needs more validation
      mock_query.return_value = [self.mock_ldap_result_user]
      user_ldap_result = self.userdata.ldap_search_user_by_username('any_valid_string')
      self.assertIsInstance(user_ldap_result, type(('a','tuple')))

   @patch.object(UserData, 'ldap_search')
   def test_group_search(self,mock_query):
      # reject multiple search results
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_group, self.mock_ldap_result_group]
         user_ldap_result = self.userdata.ldap_search_group_by_gid('any_valid_string')
      # reject group record without required attributes
      with self.assertRaises(UserDataError):
         mock_query.return_value = [self.mock_ldap_result_group_no_desc]
         user_ldap_result = self.userdata.ldap_search_group_by_gid('any_valid_string')
      mock_query.return_value = [self.mock_ldap_result_group]
      user_ldap_result = self.userdata.ldap_search_group_by_gid('any_valid_string')
      self.assertIsInstance(user_ldap_result, type(('a','tuple')))
      
   @patch.object(UserData, 'ldap_search_group_by_gid')
   @patch.object(UserData, 'ldap_search_user_by_username')
   def test_get_user_details(self,mock_user_query,mock_group_query):
      # reject search that finds no user (should never happen: search should only be done after authentication)
      with self.assertRaises(UserDataError):
         mock_user_query.return_value  = None
         mock_group_query.return_value = self.mock_ldap_result_group
         user_details = self.userdata.get_user_details('mock_does_not_exist')
      # reject user record with uid attribute that doesn't match search term
      with self.assertRaises(UserDataError):
         mock_user_query.return_value  = self.mock_ldap_result_user
         mock_group_query.return_value = self.mock_ldap_result_group
         user_details = self.userdata.get_user_details('some_other_user')
      # reject user record with empty membership attribute
      with self.assertRaises(UserDataError):
         mock_user_query.return_value  = self.mock_ldap_result_user_empty_o
         mock_group_query.return_value = self.mock_ldap_result_group
         user_details = self.userdata.get_user_details('mock_user')
      # reject user record with membership of non-existent group
      with self.assertRaises(UserDataError):
         mock_user_query.return_value  = self.mock_ldap_result_user
         mock_group_query.return_value = None
         user_details = self.userdata.get_user_details('mock_user')
      # now test a working search, to check data returned are correct
      mock_user_query.return_value  = self.mock_ldap_result_user
      mock_group_query.return_value = self.mock_ldap_result_group
      user_details = self.userdata.get_user_details('mock_user')
      # data structure
      self.assertIsInstance( user_details,                              type({'a': 'dict'})  )
      self.assertIsInstance( user_details['username'],                  type('a string')     )
      self.assertIsInstance( user_details['memberOf'],                  type(['a', 'list'])  )
      self.assertIsInstance( user_details['memberOf'][0],               type({'a': 'dict'})  )
      self.assertIsInstance( user_details['memberOf'][0]['inst_id'],    type('a string')     )
      self.assertIsInstance( user_details['memberOf'][0]['inst_name'],  type('a string')     )
      # data values
      self.assertEqual( 'mock_user',                  user_details['username']                  )
      self.assertEqual( 'WelSanIns',                  user_details['memberOf'][0]['inst_id']    )
      self.assertEqual( 'Wellcome Sanger Institute',  user_details['memberOf'][0]['inst_name']  )
