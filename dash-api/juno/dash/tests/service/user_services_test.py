from   datetime         import datetime
from   unittest         import TestCase
from   unittest.mock    import patch, Mock
import logging

from   DataServices.user_services   import MonocleUser
from   DataSources.user_data        import UserData

class MonocleUserTest(TestCase):

   test_config             = 'dash/tests/mock_data/data_sources.yml'
   mock_ldap_result_user   = (   'cn=mock_user_sanger_ac_uk,ou=users,dc=monocle,dc=pam,dc=sanger,dc=ac,dc=uk',
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
   mock_ldap_result_group  = (   'cn=WelSanIns,ou=groups,dc=monocle,dc=dev,dc=pam,dc=sanger,dc=ac,dc=uk',
                                 {  'cn': [b'WelSanIns'],
                                    'description': [b'Wellcome Sanger Institute'],
                                    'gidNumber': [b'501'],
                                    'objectClass': [b'posixGroup', b'top'],
                                    'memberUid': [b'UK']
                                    }
                                 )

   def setUp(self):
      self.user = MonocleUser(set_up=False)
      self.user.user_data.set_up(self.test_config)

   def test_init(self):
      self.assertIsInstance(self.user, MonocleUser)

   @patch.object(UserData, 'ldap_search_group_by_gid')
   @patch.object(UserData, 'ldap_search_user_by_username')
   def test_load_user_record(self,mock_user_query,mock_group_query):
      mock_user_query.return_value  = self.mock_ldap_result_user
      mock_group_query.return_value = self.mock_ldap_result_group
      user_record = self.user.load_user_record('mock_user')
      self.assertIsInstance(user_record, type({'a': 'dict'}))
      self.assertIsInstance( user_record,                                 type({'a': 'dict'})  )
      self.assertIsInstance( user_record['username'],                     type('a string')     )
      self.assertIsInstance( user_record['memberOf'],                     type(['a', 'list'])  )
      self.assertIsInstance( user_record['memberOf'][0],                  type({'a': 'dict'})  )
      self.assertIsInstance( user_record['memberOf'][0]['inst_id'],       type('a string')     )
      self.assertIsInstance( user_record['memberOf'][0]['inst_name'],     type('a string')     )
      self.assertIsInstance( user_record['memberOf'][0]['country_names'], type(['a', 'list'])  )
      # data values
      self.assertEqual( 'mock_user',                  user_record['username']                      )
      self.assertEqual( 'WelSanIns',                  user_record['memberOf'][0]['inst_id']        )
      self.assertEqual( 'Wellcome Sanger Institute',  user_record['memberOf'][0]['inst_name']      )
      self.assertEqual( ['UK'],                       user_record['memberOf'][0]['country_names']  )
