from   datetime   import datetime

import DataSources.user_data

class MonocleUser:
   """
   Provides a wrapper for claasses the retrieve user details
   Only use this after authentication: trying to get details of users that are not in LDAP will raise an exception
   """

   def __init__(self, authenticated_username=None, set_up=True):
      self.updated      = datetime.now()
      self.user_data    = DataSources.user_data.UserData(set_up=set_up)
      # only attempt to load if set_up flag is true
      if authenticated_username is not None and set_up:
         self.load_user_record(authenticated_username)

   def load_user_record(self, authenticated_username):
      self.record = self.user_data.get_user_details(authenticated_username)
      return self.record
